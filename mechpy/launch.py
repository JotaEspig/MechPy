import math

import krpc
from krpc.services import spacecenter

from mechpy import maneuver


class Launch:
    def __init__(self,
                 conn: krpc.Client,
                 vessel: spacecenter.Vessel,
                 target_alt: int,
                 turn_start_alt: int,
                 turn_end_alt: int) -> None:
        self.conn = conn
        self.vessel = vessel
        self.target_alt = target_alt
        self.turn_start_alt = turn_start_alt
        self.turn_end_alt = turn_end_alt

        # streams
        self.ut_stream = self.conn.add_stream(
            getattr, self.conn.space_center, "ut"
        )
        self.throttle_stream = self.conn.add_stream(
            getattr, self.vessel.control, "throttle"
        )
        self.altitude_stream = self.conn.add_stream(
            getattr, self.vessel.flight(None), "mean_altitude"
        )
        self.apoapsis_stream = self.conn.add_stream(
            getattr, self.vessel.orbit, "apoapsis_altitude"
        )
        self.time_to_apoapsis_stream = self.conn.add_stream(
            getattr, self.vessel.orbit, "time_to_apoapsis"
        )

    def __del__(self) -> None:
        self.ut_stream.remove()
        self.throttle_stream.remove()
        self.altitude_stream.remove()
        self.apoapsis_stream.remove()
        self.time_to_apoapsis_stream.remove()


    def do(self) -> None:
        self.vessel.control.throttle = 1
        self.vessel.auto_pilot.reference_frame = self.vessel.surface_reference_frame
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90)

        while (True):
            self.do_gravitational_turn()
            if self.apoapsis_stream() > self.target_alt:
                break

        # turn off the engines and waits to be out of atmosphere
        self.vessel.control.throttle = 0
        atmosphere_alt = self.vessel.orbit.body.atmosphere_depth
        while self.altitude_stream() <= atmosphere_alt:
            # check if apoapsis is inside the atmosphere and the burn
            if self.apoapsis_stream() <= atmosphere_alt and self.throttle_stream() < 1:
                self.vessel.control.throttle = 1

        # do the final maneuver
        delta_v = self.get_delta_v_necessary()
        node = self.vessel.control.add_node(
            self.ut_stream() + self.vessel.orbit.time_to_apoapsis, delta_v
        )
        maneuver.Maneuver(self.conn, self.vessel, node).do()
        self.reset_auto_pilot()

    def do_gravitational_turn(self) -> None:
        current_altitude = self.altitude_stream()
        should_do = current_altitude >= self.turn_start_alt \
                    and current_altitude <= self.turn_end_alt

        if should_do:
            frac = (current_altitude - self.turn_start_alt) \
                    / (self.turn_end_alt - self.turn_start_alt)
            turn_angle = frac * 90
            self.vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)

    def get_delta_v_necessary(self) -> float:
        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        # speed at apoapsis
        v1 = math.sqrt(mu * ((2 / r) - (1 / a1)))
        # speed needed to be in orbit at 'r'
        v2 = math.sqrt(mu * ((2 / r) - (1 / a2)))
        delta_v = v2 - v1
        return delta_v

    def reset_auto_pilot(self) -> None:
        self.vessel.auto_pilot.disengage()
        self.vessel.control.sas = True
