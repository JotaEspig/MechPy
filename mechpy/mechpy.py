from time import sleep
from math import exp

import krpc

from mechpy.maneuver import Maneuver


class MechPy:
    def __init__(self):
        self.conn: krpc.Client = krpc.connect(name="MechPy")
    
    def __del__(self):
        self.conn.close()

    def do_maneuver(self):
        vessel = self.conn.space_center.active_vessel
        node = vessel.control.nodes[0]
        Maneuver(self.conn, vessel, node).do()
