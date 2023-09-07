from time import sleep
from math import exp

import krpc
from krpc import stream
from krpc.services import spacecenter


class Maneuver:
    def __init__(self, conn: krpc.Client,
                 vessel: spacecenter.Vessel,
                 node: spacecenter.Node) -> None:
        self.conn = conn
        self.vessel = vessel
        self.node = node
        self.time_to_stream = self.conn.add_stream(getattr, node, "time_to")
        self.remaining_burn_stream = self.conn.add_stream(node.remaining_burn_vector, None)
    
    def __del__(self) -> None:
        self.time_to_stream.remove()
        self.remaining_burn_stream.remove()


    def do(self) -> None:
        delta_v = self.node.delta_v
        gravity = self.vessel.orbit.body.surface_gravity
        burn_time = Maneuver.get_burn_time(self.vessel, delta_v, gravity)

        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.reference_frame = self.node.reference_frame
        self.vessel.auto_pilot.target_direction = (0, 1, 0)
        self.vessel.auto_pilot.wait()

        # waits until the vessel is ready to start the burn
        while self.time_to_stream() - (burn_time / 2) > 0:
            ...

        self.vessel.control.throttle = 1
        time_to_sleep = burn_time - 0.75
        sleep(time_to_sleep)

        self.vessel.control.throttle = 0.5
        while Maneuver.should_keep_burning(self.remaining_burn_stream, 5):
            ...

        self.vessel.control.throttle = 0.05
        while Maneuver.should_keep_burning(self.remaining_burn_stream, 0.5):
            ...

        self.vessel.control.throttle = 0.01
        while Maneuver.should_keep_burning(self.remaining_burn_stream, 0.1):
            ...
        
        self.vessel.control.throttle = 0
        self.node.remove()

        self.vessel.auto_pilot.disengage()
        self.vessel.control.sas = True


    @staticmethod
    def get_burn_time(vessel: spacecenter.Vessel,
                      delta_v: float,
                      gravity: float) -> float:
        f = vessel.available_thrust
        isp = vessel.specific_impulse * gravity
        m0 = vessel.mass
        m1 = m0 / exp(delta_v / isp)
        flow_rate = f / isp
        return (m0 - m1) / flow_rate

    @staticmethod
    def should_keep_burning(stream: stream.Stream, value) -> bool:
        remaining = stream()
        return (remaining[0] > value)       \
                or (remaining[1] > value)   \
                or (remaining[2] > value)
