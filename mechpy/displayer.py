from typing import Tuple, List

import krpc
from krpc.services import ui


class Displayer:
    RECT_SIZE = (300, 200)

    def __init__(self, conn: krpc.Client) -> None:
        canvas = conn.ui.stock_canvas
        screen_size = canvas.rect_transform.size

        self.conn = conn
        self.panel = canvas.add_panel()
        self.rect = self.panel.rect_transform
        self.rect.size = self.RECT_SIZE
        self.rect.position = (110 - (screen_size[0]/2), 0)
        self.texts: List[ui.Text] = []

    def __del__(self) -> None:
        if self.conn != None:
            self.conn.ui.clear()

    def add_text(self, content: str,
                 pos: Tuple[float, float] = (0, 0),
                 color: Tuple[float, float, float] = (0, 0, 0),
                 font_size: int = 18) -> int:
        text = self.panel.add_text(content)
        text.rect_transform.position = pos
        text.color = color
        text.size = font_size

        self.texts.append(text)
        return len(self.texts) - 1

    def update_text_content(self, idx: int, content: str) -> None:
        if len(self.texts) <= idx:
            raise Exception("Invalid index to Displayer.texts")

        self.texts[idx].content = content
