import krpc


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

    def __del__(self) -> None:
        if self.conn != None:
            self.conn.ui.clear()
