"""항상 위에 떠 있는 안전창.

커서가 다른 곳에 없어서 타이핑이 어디에도 들어가지 않았더라도,
인식된 텍스트는 전부 이 창에 남는다. 나중에 드래그해서 복사해 쓸 수 있다.
"""

import queue
import threading
import time
import tkinter as tk

import config


class SafetyWindow:
    def __init__(self):
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._ready = threading.Event()
        self._root = None
        self._text = None

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
            "[voice-typer] 대기 중... F2를 눌러 녹음을 시작하세요.\n"
            "여기 적힌 내용은 전부 남아있으니, 커서가 없는 곳에서 말해도 안전합니다.\n\n",
        )

        self._poll()
        self._root.mainloop()

    def append(self, text: str):
        """다른 스레드에서 호출해서 안전창에 한 줄 추가하기."""
        self._queue.put(text)

    def _poll(self):
        try:
            while True:
                text = self._queue.get_nowait()
                timestamp = time.strftime("%H:%M:%S")
                self._text.insert("end", f"[{timestamp}] {text}\n")
                self._text.see("end")
        except queue.Empty:
            pass
        if self._root is not None:
            self._root.after(150, self._poll)
