"""항상 위에 떠 있는 안전창 + 녹음 상태를 보여주는 작은 표시등.

안전창: 커서가 다른 곳에 없어서 타이핑이 어디에도 들어가지 않았더라도,
        인식된 텍스트는 전부 이 창에 남는다. 나중에 드래그해서 복사해 쓸 수 있다.
        최소화해놔도 상관없다.

표시등: 화면 구석에 떠 있는 작은 원. 녹음 중엔 빨간색, 아닐 땐 반투명 회색이
        되어서 안전창을 열어보지 않아도 녹음 상태를 바로 확인할 수 있다.
        클릭도 그대로 아래 창으로 통과되게(click-through) 만들어서 작업에
        방해되지 않는다.

        원형 모양은 Tk의 "-transparentcolor"(컬러키 방식)가 아니라, 윈도우
        자체를 타원형으로 잘라내는 SetWindowRgn을 쓴다. 컬러키 방식은 Tk/윈도우
        조합에 따라 안 먹혀서 사각형 검은 박스로 보이는 문제가 있었다.
        반투명은 "-alpha"(창 전체 투명도)로 처리한다.
"""

import queue
import sys
import threading
import time
import tkinter as tk

import config


def _make_click_through(window: tk.Toplevel):
    """윈도우에서만: 이 창을 클릭이 그대로 통과하는(안 걸리는) 창으로 만든다.
    실패해도(다른 OS 등) 그냥 무시하고 평범한 창으로 남는다."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020

        hwnd = window.winfo_id()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT
        )
    except Exception:
        pass


def _make_circular(window: tk.Toplevel, size: int):
    """윈도우 자체를 지름 size인 원 모양으로 잘라낸다. Tk의 -transparentcolor
    (컬러키 투명) 방식보다 훨씬 안정적으로 동작한다."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        hwnd = window.winfo_id()
        hrgn = ctypes.windll.gdi32.CreateEllipticRgn(0, 0, size, size)
        ctypes.windll.user32.SetWindowRgn(hwnd, hrgn, True)
    except Exception:
        pass


class SafetyWindow:
    def __init__(self):
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._state_queue: "queue.Queue[bool]" = queue.Queue()
        self._root = None
        self._text = None
        self._indicator = None
        self._indicator_canvas = None

    def start(self):
        """반드시 메인 스레드에서 호출 (tkinter 제약)."""
        self._root = tk.Tk()
        self._root.title("voice-typer 안전창")
        self._root.geometry(config.SAFETY_WINDOW_GEOMETRY)
        self._root.attributes("-topmost", True)

        self._text = tk.Text(self._root, wrap="word", font=("Malgun Gothic", 12))
        self._text.pack(fill="both", expand=True)
        self._text.insert(
            "end",
            f"[voice-typer] 대기 중... {config.HOTKEY} 키를 눌러 녹음을 시작하세요.\n"
            "여기 적힌 내용은 전부 남아있으니, 커서가 없는 곳에서 말해도 안전합니다.\n"
            "이 창은 최소화해도 되고, 화면 구석의 작은 점으로 녹음 상태를 확인할 수 있습니다.\n\n",
        )

        if config.INDICATOR_ENABLED:
            self._build_indicator()

        self._poll()
        self._root.mainloop()

    def _build_indicator(self):
        size = config.INDICATOR_SIZE
        margin = config.INDICATOR_MARGIN

        self._indicator = tk.Toplevel(self._root)
        self._indicator.overrideredirect(True)
        self._indicator.attributes("-topmost", True)
        try:
            self._indicator.attributes("-alpha", config.INDICATOR_OPACITY)
        except tk.TclError:
            pass  # 일부 환경에선 창 투명도 속성이 없을 수 있음 - 불투명하게 남음

        screen_w = self._indicator.winfo_screenwidth()
        screen_h = self._indicator.winfo_screenheight()
        x, y = _corner_position(config.INDICATOR_CORNER, screen_w, screen_h, size, margin)
        self._indicator.geometry(f"{size}x{size}+{x}+{y}")

        self._indicator_canvas = tk.Canvas(
            self._indicator,
            width=size,
            height=size,
            bg=config.INDICATOR_COLOR_IDLE,
            highlightthickness=0,
        )
        self._indicator_canvas.pack()

        self._indicator.update_idletasks()
        _make_circular(self._indicator, size)
        _make_click_through(self._indicator)

    def append(self, text: str):
        """다른 스레드에서 호출해서 안전창에 한 줄 추가하기."""
        self._queue.put(text)

    def set_recording(self, is_recording: bool):
        """다른 스레드에서 호출해서 표시등 색을 바꾸기."""
        self._state_queue.put(is_recording)

    def _poll(self):
        try:
            while True:
                text = self._queue.get_nowait()
                timestamp = time.strftime("%H:%M:%S")
                self._text.insert("end", f"[{timestamp}] {text}\n")
                self._text.see("end")
        except queue.Empty:
            pass

        try:
            while True:
                is_recording = self._state_queue.get_nowait()
                if self._indicator_canvas is not None:
                    color = (
                        config.INDICATOR_COLOR_RECORDING
                        if is_recording
                        else config.INDICATOR_COLOR_IDLE
                    )
                    self._indicator_canvas.configure(bg=color)
        except queue.Empty:
            pass

        if self._root is not None:
            self._root.after(100, self._poll)


def _corner_position(corner: str, screen_w: int, screen_h: int, size: int, margin: int):
    if corner == "top-left":
        return margin, margin
    if corner == "bottom-left":
        return margin, screen_h - size - margin
    if corner == "bottom-right":
        return screen_w - size - margin, screen_h - size - margin
    return screen_w - size - margin, margin  # top-right
