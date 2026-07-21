"""voice-typer: F2로 켜고 끄는 음성 타이핑 시스템.

동작:
  1. F2를 누르면 녹음 시작, 다시 누르면 녹음 종료 (config.MODE == "toggle").
     또는 F2로 "상시 감지 모드" on/off, 그 안에서는 소리 크기로 자동 문장 구분
     (config.MODE == "vad").
  2. 녹음이 끝난 구간을 faster-whisper(turbo, GPU)로 텍스트 변환.
  3. 변환된 텍스트를 (a) 현재 커서/포커스가 있는 곳에 실제로 타이핑하고,
     (b) 항상 떠 있는 안전창(overlay)에도 남긴다. 커서가 없어서 (a)가
     실패해도 (b) 덕분에 텍스트가 사라지지 않는다.

주의: GPU(NVIDIA, VRAM 8GB+)와 마이크가 있는 실제 PC에서 실행해야 한다.
      이 코드는 개발 환경(원격 리눅스 샌드박스, GPU/마이크 없음)에서
      문법 확인만 했고, 실제 녹음·GPU 추론·전역 단축키 동작은 검증하지
      못했다. 로컬에서 처음 실행할 때는 README의 점검 순서를 따라
      단계별로 확인할 것.
"""

import queue
import sys
import threading
import time

import numpy as np
import sounddevice as sd
import keyboard
from faster_whisper import WhisperModel

import config
from overlay import SafetyWindow


def rms_dbfs(block: np.ndarray) -> float:
    """float32 [-1, 1] 오디오 블록의 대략적인 dBFS(RMS 기준) 값."""
    rms = np.sqrt(np.mean(np.square(block)) + 1e-12)
    return 20 * np.log10(rms + 1e-12)


class VoiceTyper:
    def __init__(self, safety_window: SafetyWindow):
        self.safety_window = safety_window
        self.safety_window.append(f"[모델 로딩 중] {config.MODEL_SIZE} / {config.DEVICE}")

        self.model = WhisperModel(
            config.MODEL_SIZE,
            device=config.DEVICE,
            compute_type=config.COMPUTE_TYPE,
        )
        self.safety_window.append("[모델 로딩 완료] F2를 눌러 녹음을 시작하세요.")

        self.recording = False
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    # ---------------- 공통: 녹음 -> 변환 -> 출력 ----------------

    def _transcribe_and_emit(self, audio: np.ndarray):
        if audio.size == 0:
            return
        duration = audio.size / config.SAMPLE_RATE
        if duration < 0.2:
            return  # 너무 짧은 잡음성 구간은 무시

        segments, _info = self.model.transcribe(
            audio,
            language=config.LANGUAGE,
            vad_filter=True,
        )
        text = "".join(seg.text for seg in segments).strip()
        if not text:
            return

        self.safety_window.append(text)
        if config.TYPE_AT_CURSOR:
            try:
                keyboard.write(text + " ")
            except Exception as exc:  # 타이핑 실패해도 안전창엔 이미 남아있음
                self.safety_window.append(f"[타이핑 실패: {exc}]")

    def _run_transcription_async(self, audio: np.ndarray):
        threading.Thread(target=self._transcribe_and_emit, args=(audio,), daemon=True).start()

    # ---------------- MODE == "toggle" ----------------

    def _audio_callback(self, indata, frames, time_info, status):
        with self._lock:
            self._frames.append(indata.copy().reshape(-1))

    def toggle_recording(self):
        with self._lock:
            starting = not self.recording
            self.recording = starting

        if starting:
            self._frames = []
            self._stream = sd.InputStream(
                samplerate=config.SAMPLE_RATE,
                channels=1,
                dtype="float32",
                callback=self._audio_callback,
            )
            self._stream.start()
            self.safety_window.append("[녹음 시작]")
        else:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self.safety_window.append("[녹음 종료 - 변환 중...]")
            with self._lock:
                audio = np.concatenate(self._frames) if self._frames else np.array([], dtype="float32")
                self._frames = []
            self._run_transcription_async(audio)

    # ---------------- MODE == "vad" ----------------

    def _vad_loop(self, stop_event: threading.Event):
        block_size = int(config.SAMPLE_RATE * config.VAD_BLOCK_MS / 1000)
        speaking = False
        silence_ms = 0
        buffer: list[np.ndarray] = []

        with sd.InputStream(
            samplerate=config.SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=block_size,
        ) as stream:
            while not stop_event.is_set():
                block, _overflow = stream.read(block_size)
                block = block.reshape(-1)
                level = rms_dbfs(block)

                if level >= config.VAD_DB_THRESHOLD:
                    if not speaking:
                        speaking = True
                        self.safety_window.append("[말 시작 감지]")
                    buffer.append(block)
                    silence_ms = 0
                elif speaking:
                    buffer.append(block)
                    silence_ms += config.VAD_BLOCK_MS
                    if silence_ms >= config.VAD_SILENCE_MS:
                        audio = np.concatenate(buffer)
                        buffer = []
                        speaking = False
                        silence_ms = 0
                        self.safety_window.append("[문장 종료 - 변환 중...]")
                        self._run_transcription_async(audio)

    def toggle_vad(self):
        with self._lock:
            starting = not self.recording
            self.recording = starting

        if starting:
            self._vad_stop_event = threading.Event()
            self._vad_thread = threading.Thread(
                target=self._vad_loop, args=(self._vad_stop_event,), daemon=True
            )
            self._vad_thread.start()
            self.safety_window.append(
                f"[상시 감지 모드 ON] 기준 {config.VAD_DB_THRESHOLD} dBFS"
            )
        else:
            self._vad_stop_event.set()
            self._vad_thread.join(timeout=2)
            self.safety_window.append("[상시 감지 모드 OFF]")


def main():
    safety_window = SafetyWindow()

    # 모델 로딩과 녹음 관련 객체 생성은 tkinter 창이 뜬 뒤 별도 스레드에서 진행해야
    # 무거운 모델 로딩 중에도 창이 멈춘 것처럼 보이지 않는다.
    def setup_and_bind():
        typer = VoiceTyper(safety_window)

        if config.MODE == "toggle":
            keyboard.add_hotkey(config.HOTKEY, typer.toggle_recording)
        elif config.MODE == "vad":
            keyboard.add_hotkey(config.HOTKEY, typer.toggle_vad)
        else:
            print(f"알 수 없는 MODE: {config.MODE}", file=sys.stderr)
            sys.exit(1)

    threading.Thread(target=setup_and_bind, daemon=True).start()

    safety_window.start()  # 메인 스레드에서 tkinter mainloop 실행 (블로킹)


if __name__ == "__main__":
    main()
