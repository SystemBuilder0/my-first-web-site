"""voice-typer 설정 파일. 값만 바꿔서 쓰면 됨."""

# F2를 누르면 녹음 시작/종료가 토글됨 (keyboard 라이브러리 키 이름 규칙 사용)
HOTKEY = "f2"

# "toggle": F2로 수동 시작/종료 (기본, 쉬움)
# "vad":    F2로 "상시 감지 모드"를 켜고 끄기만 하고, 그 안에서는 소리 크기(dB)로 자동 시작/종료
MODE = "toggle"

# faster-whisper 모델 크기. "turbo" = large-v3-turbo, 속도 우선.
# 정확도를 더 원하면 "large-v3", 가벼운 GPU(VRAM 부족)면 "medium"/"small"로 낮추면 됨.
MODEL_SIZE = "turbo"

# "cuda" = GPU 사용 (RTX 3060 이상, VRAM 8GB+ 권장). GPU가 없거나 인식 안 되면 "cpu"로 바꾸되
# CPU는 turbo 모델도 체감상 많이 느림.
DEVICE = "cuda"

# GPU float16이 가장 빠르고 8GB VRAM에서도 turbo 모델엔 넉넉함.
# CPU로 돌릴 때는 "int8"을 추천.
COMPUTE_TYPE = "float16"

# 한국어 고정. 다국어 자동감지를 원하면 None으로.
LANGUAGE = "ko"

SAMPLE_RATE = 16000

# ---- MODE = "vad" 일 때만 사용되는 값들 ----
# 이 dB(대략적인 RMS 기준 dBFS)보다 크게 들리면 "말하는 중"으로 판단.
# 마이크/환경마다 다르므로 실제로 켜보고 로그에 찍히는 값을 보면서 조정할 것.
VAD_DB_THRESHOLD = -40

# 말이 끊긴 뒤 이만큼(ms) 조용하면 "한 문장 끝"으로 보고 바로 텍스트 변환 시작.
VAD_SILENCE_MS = 700

# 녹음 시작 판단을 위해 오디오를 검사하는 블록 길이(ms).
VAD_BLOCK_MS = 30

# 커서가 있는 곳(현재 포커스된 창)에 실제로 타이핑까지 할지 여부.
# False로 하면 안전창(safety window)에만 기록되고 실제 타이핑은 안 됨.
TYPE_AT_CURSOR = True

# 안전창(모든 인식 결과가 항상 남는 별도의 항상-위-창) 크기
SAFETY_WINDOW_GEOMETRY = "480x320+40+40"
