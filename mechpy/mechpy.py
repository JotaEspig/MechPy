import krpc

from mechpy import displayer
from mechpy import launch
from mechpy import maneuver
from mechpy import suicideburn
from mechpy.__version__ import __version__


class MechPy:
    def __init__(self):
        conn = krpc.connect(name="MechPy")
        screen_size = conn.ui.stock_canvas.rect_transform.size

        self.conn = conn
        self.conn.ui.message(f"MechPy\nVersion: v{__version__}", duration=5)
        self.display = displayer.Displayer(
            self.conn, (300, 200), (151 - screen_size[0]/2, 200)
        )

    def __del__(self):
        if self.conn != None:
            del self.display
            self.conn.ui.message("MechPy closed", duration=5)
            self.conn.ui.clear()
            self.conn.close()

    def do_maneuver(self):
        self.conn.ui.message("Doing maneuver", duration=2)

        vessel = self.conn.space_center.active_vessel
        if len(vessel.control.nodes) == 0:
            return

        node = vessel.control.nodes[0]
        maneuver.Maneuver(self.conn, vessel, node).do()

    def launch_into_orbit(self, target_alt: int, turn_start_alt: int,
                          turn_end_alt: int) -> None:
        self.conn.ui.message("Launching into orbit", duration=2)

        vessel = self.conn.space_center.active_vessel
        launch.Launch(
            self.conn, vessel, target_alt, turn_start_alt, turn_end_alt
        ).do()

    def suicide_burn(self) -> None:
        self.conn.ui.message(
            "Doing SUICIDE BURN\nI hope we don't crash", duration=2)

        vessel = self.conn.space_center.active_vessel
        suicideburn.SuicideBurn(self.conn, vessel).do()
