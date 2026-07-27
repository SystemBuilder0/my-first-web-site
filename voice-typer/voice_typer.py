"""voice-typer: F2로 켜고 끄는 음성 타이핑 시스템.

동작:
  1. F2를 누르면 녹음 시작, 다시 누르면 녹음 종료 (config.MODE == "toggle").
     또는 F2로 "상시 감지 모드" on/off, 그 안에서는 소리 크기로 자동 문장 구분
     (config.MODE == "vad").
  2. 녹음이 끝난 구간을 faster-whisper(turbo, GPU)로 텍스트 변환.
  3. 변환된 텍스트를 (a) 현재 커서/포커스가 있는 곳에 실제로 타이핑하고,
     (b) 항상 떠 있는 안전창(overlay)에도 남긴다. 커서가 없어서 (a)가
     실패해도 (b) 덕분에 텍스트가 사라지지 않는다.

오디오 입력은 sounddevice(PortAudio)가 아니라 soundcard(WASAPI) 라이브러리를
쓴다. PortAudio는 초기화할 때 WDM-KS 등 모든 오디오 백엔드의 장치를 훑는데,
일부 다채널 오디오 인터페이스(예: Antelope ZenGo SC) 드라이버에서 이 과정이
그대로 프로세스를 죽여버리는 문제가 있었다. soundcard는 WASAPI만 쓰기 때문에
이 문제를 피해간다 (Premiere Pro 등 일반 프로그램도 WASAPI/ASIO로 접근해서
문제없이 녹음되는 것과 같은 이유).

주의: GPU(NVIDIA, VRAM 8GB+)와 마이크가 있는 실제 PC에서 실행해야 한다.
      이 코드는 개발 환경(원격 리눅스 샌드박스, GPU/마이크 없음)에서
      문법 확인만 했고, 실제 녹음·GPU 추론·전역 단축키 동작은 검증하지
      못했다. 로컬에서 처음 실행할 때는 README의 점검 순서를 따라
      단계별로 확인할 것.
"""

import os
import sys
import threading
import time
from typing import List, NamedTuple


def _register_nvidia_dll_dirs():
    """pip로 설치된 nvidia-* 패키지(cublas, cudnn, cuda_nvrtc 등)의 DLL 폴더를
    이 프로세스가 찾을 수 있게 등록한다. faster_whisper를 import하기 전에 실행해야 한다.

    두 가지 방법을 모두 쓴다:
      1) os.add_dll_directory  - 파이썬 확장 모듈(.pyd) 로딩용 표준 방식.
      2) os.environ['PATH'] 앞에 직접 추가 - ctranslate2는 cublas64_12.dll을
         실행 도중 옛날 방식(LoadLibrary)으로 부르는데, 이건 add_dll_directory로
         추가한 경로를 참조하지 않는다. 그래서 PATH에도 직접 넣어야 확실히 찾는다.
         (예전에 'set PATH=...'를 손으로 했을 때만 됐던 이유가 이것이다.)
    """
    if sys.platform != "win32":
        return
    try:
        import nvidia
    except ImportError:
        return

    bin_dirs = []
    for base in list(getattr(nvidia, "__path__", [])):
        if not os.path.isdir(base):
            continue
        for sub in os.listdir(base):  # cublas, cudnn, cuda_nvrtc, ...
            bin_dir = os.path.join(base, sub, "bin")
            if os.path.isdir(bin_dir):
                bin_dirs.append(bin_dir)

    for bin_dir in bin_dirs:
        try:
            os.add_dll_directory(bin_dir)
        except OSError:
            pass
    if bin_dirs:
        os.environ["PATH"] = os.pathsep.join(bin_dirs) + os.pathsep + os.environ.get("PATH", "")


_register_nvidia_dll_dirs()

import numpy as np
import soundcard as sc
import keyboard
from faster_whisper import WhisperModel

import config
from overlay import SafetyWindow


def rms_dbfs(block: np.ndarray) -> float:
    """float32 [-1, 1] 오디오 블록의 대략적인 dBFS(RMS 기준) 값."""
    rms = np.sqrt(np.mean(np.square(block)) + 1e-12)
    return 20 * np.log10(rms + 1e-12)


# ---------------- 실시간(stream) 모드용 순수 계산 함수들 ----------------
# 아래 세 함수는 오디오/GPU와 무관한 순수 로직이라 따로 테스트할 수 있다.


class SWord(NamedTuple):
    """인식된 단어 하나. start/end는 '녹음 시작 시점'을 0으로 하는 절대 시각(초)."""

    text: str
    start: float
    end: float


def normalize_word(text: str) -> str:
    """두 인식 결과의 단어가 '같은 단어'인지 비교하기 위한 정규화.
    앞뒤 공백과 문장부호는 자주 바뀌므로 무시한다."""
    return text.strip().strip(".,!?;:\"'()[]{}…·~-").strip().lower()


def agreed_prefix_len(prev: List[SWord], curr: List[SWord]) -> int:
    """연속된 두 번의 인식 결과에서, 앞에서부터 몇 개의 단어가 서로 일치하는지.
    이 개수만큼만 '확정'해서 타이핑한다 (LocalAgreement)."""
    n = 0
    for a, b in zip(prev, curr):
        na, nb = normalize_word(a.text), normalize_word(b.text)
        if na and na == nb:
            n += 1
        else:
            break
    return n


def words_after(words: List[SWord], t: float, eps: float = 0.02) -> List[SWord]:
    """시각 t까지는 이미 확정(타이핑)됐으므로, 그 뒤에 오는 단어만 남긴다."""
    return [w for w in words if w.end > t + eps]


def pick_microphone(safety_window: SafetyWindow):
    """config.MIC_NAME과 이름이 겹치는 마이크를 고르고, 없으면 시스템 기본 마이크."""
    if config.MIC_NAME:
        try:
            mic = sc.get_microphone(config.MIC_NAME, include_loopback=False)
            safety_window.append(f"[마이크 선택] {mic.name}")
            return mic
        except Exception as exc:
            safety_window.append(
                f"[마이크 '{config.MIC_NAME}'을 못 찾음: {exc} - 기본 마이크로 대체]"
            )
    mic = sc.default_microphone()
    safety_window.append(f"[마이크 선택 - 기본값] {mic.name}")
    return mic


class VoiceTyper:
    def __init__(self, safety_window: SafetyWindow):
        self.safety_window = safety_window

        self.mic = pick_microphone(safety_window)

        self.safety_window.append(f"[모델 로딩 중] {config.MODEL_SIZE} / {config.DEVICE}")
        self.model = WhisperModel(
            config.MODEL_SIZE,
            device=config.DEVICE,
            compute_type=config.COMPUTE_TYPE,
        )
        self.safety_window.append("[모델 로딩 완료] F2를 눌러 녹음을 시작하세요.")

        self.recording = False
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._stop_event: threading.Event | None = None
        self._record_thread: threading.Thread | None = None
        self._stream_thread: threading.Thread | None = None

    # ---------------- 공통: 녹음 -> 변환 -> 출력 ----------------

    def _type(self, text: str):
        """커서 위치에 실제로 타이핑. 실패해도 프로그램은 계속 돈다."""
        if not text or not config.TYPE_AT_CURSOR:
            return
        try:
            keyboard.write(text)
        except Exception as exc:  # 타이핑 실패해도 안전창엔 남는다
            self.safety_window.append(f"[타이핑 실패: {exc}]")

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
            self.safety_window.append("[인식된 말이 없음]")
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

    def _record_loop(self, stop_event: threading.Event):
        block_size = int(config.SAMPLE_RATE * 0.05)  # 50ms 씩 읽음
        with self.mic.recorder(samplerate=config.SAMPLE_RATE, channels=1) as rec:
            while not stop_event.is_set():
                data = rec.record(numframes=block_size)
                with self._lock:
                    self._frames.append(data.reshape(-1).astype("float32"))

    def toggle_recording(self):
        with self._lock:
            starting = not self.recording
            self.recording = starting

        if starting:
            self._frames = []
            self._stop_event = threading.Event()
            self._record_thread = threading.Thread(
                target=self._record_loop, args=(self._stop_event,), daemon=True
            )
            self._record_thread.start()
            self.safety_window.append("[녹음 시작]")
            self.safety_window.set_recording(True)
        else:
            self._stop_event.set()
            self._record_thread.join(timeout=5)
            self.safety_window.append("[녹음 종료 - 변환 중...]")
            self.safety_window.set_recording(False)
            with self._lock:
                audio = np.concatenate(self._frames) if self._frames else np.array([], dtype="float32")
                self._frames = []
            self._run_transcription_async(audio)

    # ---------------- MODE == "stream" (실시간 타이핑) ----------------

    def _transcribe_words(self, audio: np.ndarray, offset: float) -> List[SWord]:
        """오디오를 인식해서 단어 목록으로 돌려준다.
        offset은 이 오디오 버퍼의 첫 샘플이 '녹음 시작'으로부터 몇 초 뒤인지 (앞부분을
        잘라냈을 수 있으므로), 단어 시각을 절대 시각으로 맞추는 데 쓴다."""
        segments, _info = self.model.transcribe(
            audio,
            language=config.LANGUAGE,
            vad_filter=True,
            word_timestamps=True,
            # 실시간에서는 같은 구간을 반복해서 인식하므로, 직전 문맥에 끌려가
            # 결과가 흔들리지 않도록 끈다.
            condition_on_previous_text=False,
            beam_size=config.STREAM_BEAM_SIZE,
        )
        words: List[SWord] = []
        for seg in segments:
            for w in (seg.words or []):
                if w.word.strip():
                    words.append(SWord(w.word, w.start + offset, w.end + offset))
        return words

    def _stream_worker(self, stop_event: threading.Event):
        """말하는 도중에도 계속 인식해서, 확정된 부분만 바로 타이핑한다."""
        offset = 0.0          # 현재 버퍼 맨 앞이 녹음 시작으로부터 몇 초 지점인지
        last_end = 0.0        # 여기까지는 이미 확정(타이핑)했다는 절대 시각
        prev_words: List[SWord] = []
        session_text = ""
        first_commit = True
        next_run = time.monotonic()

        while True:
            stopping = stop_event.is_set()
            if not stopping and time.monotonic() < next_run:
                time.sleep(0.02)
                continue

            with self._lock:
                audio = (
                    np.concatenate(self._frames)
                    if self._frames
                    else np.zeros(0, dtype="float32")
                )

            if audio.size < int(config.SAMPLE_RATE * config.STREAM_MIN_AUDIO_SEC):
                if stopping:
                    break
                next_run = time.monotonic() + config.STREAM_INTERVAL_SEC
                continue

            try:
                words = self._transcribe_words(audio, offset)
            except Exception as exc:
                self.safety_window.append(f"[인식 오류: {exc}]")
                if stopping:
                    break
                next_run = time.monotonic() + config.STREAM_INTERVAL_SEC
                continue

            pending = words_after(words, last_end)

            if stopping:
                # 녹음이 끝났으니 남은 것은 더 기다릴 필요 없이 전부 확정한다.
                commit = pending
            else:
                # 연속된 두 번의 결과가 일치하는 앞부분만 확정한다.
                k = agreed_prefix_len(prev_words, pending)
                # 안전장치: 녹음 맨 끝에 걸친 단어는 뒷말이 붙으면 해석이 바뀔 수
                # 있으므로, 뒤에 소리가 충분히 쌓이기 전에는 확정하지 않는다.
                buffer_end = offset + audio.size / config.SAMPLE_RATE
                stable_until = buffer_end - config.STREAM_RIGHT_CONTEXT_SEC
                while k > 0 and pending[k - 1].end > stable_until:
                    k -= 1
                commit = pending[:k]
                prev_words = pending[k:]

            if commit:
                text = "".join(w.text for w in commit)
                if first_commit:
                    text = text.lstrip()
                    first_commit = False
                self._type(text)
                session_text += text
                last_end = commit[-1].end

            if stopping:
                break

            # 버퍼가 너무 길어지면, 이미 확정된 앞부분을 잘라내서
            # 매번 다시 인식하는 양이 무한정 늘어나지 않게 한다.
            buffer_sec = audio.size / config.SAMPLE_RATE
            cut_sec = (last_end - offset) - config.STREAM_KEEP_BACK_SEC
            if buffer_sec > config.STREAM_MAX_BUFFER_SEC and cut_sec > 0:
                cut_n = int(cut_sec * config.SAMPLE_RATE)
                with self._lock:
                    current = (
                        np.concatenate(self._frames)
                        if self._frames
                        else np.zeros(0, dtype="float32")
                    )
                    self._frames = [current[cut_n:]]
                offset += cut_n / config.SAMPLE_RATE

            next_run = time.monotonic() + config.STREAM_INTERVAL_SEC

        if session_text:
            self._type(" ")  # 다음 문장과 붙지 않도록
            self.safety_window.append(session_text.strip())
        else:
            self.safety_window.append("[인식된 말이 없음]")
        self.safety_window.set_recording(False)

    def toggle_stream(self):
        with self._lock:
            starting = not self.recording
            self.recording = starting

        if starting:
            # 앞선 세션의 마무리 인식이 아직 돌고 있으면 끝날 때까지 기다린다.
            if self._stream_thread is not None and self._stream_thread.is_alive():
                self._stream_thread.join(timeout=10)

            with self._lock:
                self._frames = []
            self._stop_event = threading.Event()
            self._record_thread = threading.Thread(
                target=self._record_loop, args=(self._stop_event,), daemon=True
            )
            self._record_thread.start()
            self._stream_thread = threading.Thread(
                target=self._stream_worker, args=(self._stop_event,), daemon=True
            )
            self._stream_thread.start()
            self.safety_window.append("[녹음 시작 - 말하는 대로 바로 타이핑됩니다]")
            self.safety_window.set_recording(True)
        else:
            # stop_event만 알려주고 바로 빠져나온다. 남은 마무리 인식은
            # 백그라운드에서 끝내므로 단축키가 멈춘 것처럼 느껴지지 않는다.
            self._stop_event.set()
            self.safety_window.append("[녹음 종료 - 마무리 중...]")

    # ---------------- MODE == "vad" ----------------

    def _vad_loop(self, stop_event: threading.Event):
        block_size = int(config.SAMPLE_RATE * config.VAD_BLOCK_MS / 1000)
        speaking = False
        silence_ms = 0
        buffer: list[np.ndarray] = []

        with self.mic.recorder(samplerate=config.SAMPLE_RATE, channels=1) as rec:
            while not stop_event.is_set():
                data = rec.record(numframes=block_size)
                block = data.reshape(-1).astype("float32")
                level = rms_dbfs(block)

                if level >= config.VAD_DB_THRESHOLD:
                    if not speaking:
                        speaking = True
                        self.safety_window.append("[말 시작 감지]")
                        self.safety_window.set_recording(True)
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
                        self.safety_window.set_recording(False)
                        self._run_transcription_async(audio)

    def toggle_vad(self):
        with self._lock:
            starting = not self.recording
            self.recording = starting

        if starting:
            self._stop_event = threading.Event()
            self._record_thread = threading.Thread(
                target=self._vad_loop, args=(self._stop_event,), daemon=True
            )
            self._record_thread.start()
            self.safety_window.append(
                f"[상시 감지 모드 ON] 기준 {config.VAD_DB_THRESHOLD} dBFS"
            )
        else:
            self._stop_event.set()
            self._record_thread.join(timeout=2)
            self.safety_window.append("[상시 감지 모드 OFF]")
            self.safety_window.set_recording(False)


def main():
    safety_window = SafetyWindow()

    # 모델 로딩과 녹음 관련 객체 생성은 tkinter 창이 뜬 뒤 별도 스레드에서 진행해야
    # 무거운 모델 로딩 중에도 창이 멈춘 것처럼 보이지 않는다.
    def setup_and_bind():
        typer = VoiceTyper(safety_window)

        if config.MODE == "stream":
            keyboard.add_hotkey(config.HOTKEY, typer.toggle_stream, suppress=config.SUPPRESS_HOTKEY)
        elif config.MODE == "toggle":
            keyboard.add_hotkey(config.HOTKEY, typer.toggle_recording, suppress=config.SUPPRESS_HOTKEY)
        elif config.MODE == "vad":
            keyboard.add_hotkey(config.HOTKEY, typer.toggle_vad, suppress=config.SUPPRESS_HOTKEY)
        else:
            print(f"알 수 없는 MODE: {config.MODE}", file=sys.stderr)
            sys.exit(1)

    threading.Thread(target=setup_and_bind, daemon=True).start()

    safety_window.start()  # 메인 스레드에서 tkinter mainloop 실행 (블로킹)


if __name__ == "__main__":
    main()
