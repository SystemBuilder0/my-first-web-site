"""voice-typer 설정 파일. 값만 바꿔서 쓰면 됨."""

# 이 키를 누르면 녹음 시작/종료가 토글됨 (keyboard 라이브러리 키 이름 규칙 사용).
# F2는 오브시디언 등 여러 앱에서 "제목 바꾸기(rename)"에 쓰이지만, 아래
# SUPPRESS_HOTKEY가 켜져 있으면 그 앱으로 키 입력이 전달되지 않아서 충돌이
# 안 생긴다. 그래도 계속 겹치는 앱이 있으면 "scroll lock"이나 "pause"로
# 바꿔볼 것.
HOTKEY = "f2"

# True로 두면 HOTKEY를 누르는 순간 그 키 입력 자체가 현재 포커스된 프로그램으로
# 전달되지 않도록 막는다 (keyboard.add_hotkey의 suppress 옵션). 이렇게 해야
# 앞으로 어떤 키를 고르든 "그 앱에서도 같은 키에 다른 동작이 매핑되어 있어서
# 같이 실행돼버리는" 문제가 원천적으로 안 생긴다.
SUPPRESS_HOTKEY = True

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

# 사용할 마이크를 이름의 일부로 지정 (윈도우 "사운드 설정 > 입력"에 뜨는 이름 참고).
# 예: "ZenGo" 라고만 써도 이름에 ZenGo가 들어간 장치를 찾아서 씀.
# None으로 두면 윈도우에 설정된 기본 마이크를 그대로 씀.
MIC_NAME = "ZenGo"

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

# ---- 녹음 상태 표시등 (화면 구석의 작은 점) ----
# 안전창을 열어보지 않아도 녹음 중인지 바로 확인할 수 있는 작은 원.
# 클릭도 그대로 통과시켜서(click-through) 작업에 방해되지 않는다.
INDICATOR_ENABLED = True

# 화면 어느 구석에 둘지: "bottom-right"(기본), "top-right", "top-left", "bottom-left"
INDICATOR_CORNER = "bottom-right"

INDICATOR_SIZE = 22       # 지름(px)
# 화면 가장자리로부터 여백(px). 작업표시줄(taskbar)에 가려지면 이 값을 늘릴 것.
INDICATOR_MARGIN = 60

# 0.0(완전 투명) ~ 1.0(완전 불투명). 반투명하게 보이려면 1.0보다 낮게.
INDICATOR_OPACITY = 0.55

# 검은 화면/흰 화면/회색 화면 어디서든 묻히지 않으면서도 경고등처럼 튀지
# 않는 색을 골랐다: 채도가 높고 명도는 중간인 색(청록/teal 계열)은
# - 검은 배경보다는 밝고, 흰 배경보다는 어두워서 명도 대비가 항상 생기고
# - 배경이 무채색(회색)이어도 색상(hue) 자체가 도드라져 보인다.
# 빨강/주황처럼 "경고·긴급" 느낌을 주지 않아 은은하게 계속 떠 있어도 부담이 없다.
INDICATOR_COLOR_IDLE = "#4FD1C5"        # 대기 중: 차분한 청록색
INDICATOR_COLOR_RECORDING = "#319795"   # 녹음 중: 조금 더 진한 청록색 (색이 안 바뀌어도 깜빡임으로 구분됨)

# 녹음 중일 때 표시등의 밝기(투명도)가 사인파(sine wave)처럼 부드럽게
# 오르내리며 "맥박"치게 한다. 색 변화보다 투명도(-alpha) 변화가 이 환경에서
# 훨씬 안정적으로 화면에 반영되기 때문에, 상태 구분은 이 펄스가 담당한다.
INDICATOR_BLINK_WHILE_RECORDING = True
INDICATOR_PULSE_PERIOD_MS = 1400    # 한 번 밝아졌다 어두워지는 데 걸리는 시간(ms) - 클수록 느긋한 맥박
INDICATOR_PULSE_STEP_MS = 40        # 갱신 간격(ms) - 작을수록 더 부드럽게 보임 (25fps 정도)
INDICATOR_BLINK_ALPHA_LOW = 0.2     # 맥박의 가장 흐린 지점(0~1)
INDICATOR_BLINK_ALPHA_HIGH = 0.95   # 맥박의 가장 진한 지점(0~1)
