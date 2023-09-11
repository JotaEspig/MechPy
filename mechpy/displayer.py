from typing import Tuple, List

import krpc
from krpc import stream
from krpc.services import ui


class Displayer:
    def __init__(self, conn: krpc.Client, size: Tuple[float, float],
                 pos: Tuple[float, float]) -> None:
        canvas = conn.ui.stock_canvas
        panel = canvas.add_panel()
        rect = panel.rect_transform
        rect.size = size
        rect.position = pos

        self.conn = conn
        self.panel = panel
        self.rect = rect
        self.texts: List[ui.Text] = []
        self.buttons: List[ui.Button] = []
        self.input_fields: List[ui.InputField] = []

    def __del__(self) -> None:
        if self.conn != None:
            self.panel.remove()

    def add_text(self, content: str, pos: Tuple[float, float] = (0, 0),
                 color: Tuple[float, float, float] = (0, 0, 0),
                 font_size: int = 18) -> int:
        text = self.panel.add_text(content)
        text.rect_transform.position = pos
        text.color = color
        text.size = font_size

        self.texts.append(text)
        return len(self.texts) - 1

    def update_text_content(self, idx: int, content: str) -> None:
        self.texts[idx].content = content

    def add_button(self, content: str,
                   pos: Tuple[float, float] = (0, 0)) -> int:
        btn = self.panel.add_button(content)
        btn.rect_transform.position = pos
        self.buttons.append(btn)
        return len(self.buttons) - 1

    def get_button_clicked_stream(self, idx: int) -> stream.Stream:
        btn_stream = self.conn.add_stream(
            getattr, self.buttons[idx], "clicked"
        )
        return btn_stream

    def add_input_field(self, pos: Tuple[float, float] = (0, 0)) -> int:
        input_field = self.panel.add_input_field()
        input_field.rect_transform.position = pos
        self.input_fields.append(input_field)
        return len(self.input_fields) - 1

    def get_input_field_changed_stream(self, idx: int) -> stream.Stream:
        input_stream = self.conn.add_stream(
            getattr, self.input_fields[idx], "changed"
        )
        return input_stream
