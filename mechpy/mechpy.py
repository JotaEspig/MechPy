from time import sleep
from math import exp

import krpc

from mechpy import launch
from mechpy import maneuver
from mechpy import suicideburn

class MechPy:
    def __init__(self):
        self.conn: krpc.Client = krpc.connect(name="MechPy")
    
    def __del__(self):
        self.conn.close()


    def do_maneuver(self):
        vessel = self.conn.space_center.active_vessel
        if len(vessel.control.nodes) == 0:
            return

        node = vessel.control.nodes[0]
        maneuver.Maneuver(self.conn, vessel, node)

    def launch_into_orbit(self, target_alt: int, turn_start_alt: int,
                          turn_end_alt: int) -> None:
        vessel = self.conn.space_center.active_vessel
        launch.Launch(
            self.conn, vessel, target_alt, turn_start_alt, turn_end_alt
        ).do()

    def suicide_burn(self) -> None:
        vessel = self.conn.space_center.active_vessel
        suicideburn.SuicideBurn(self.conn, vessel).do()
