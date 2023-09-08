import krpc
from krpc.services import spacecenter


class SuicideBurn:
    FINAL_SPEED = 5
    SAFE_MARGIN_OFFSET = 15
    OFFSET_TO_HORIZONTAL_SB = 2000

    def __init__(self, conn: krpc.Client, vessel: spacecenter.Vessel) -> None:
        self.conn = conn
        self.vessel = vessel
        self.flight = self.vessel.flight(self.vessel.orbit.body.reference_frame)

        # streams
        self.thrust_stream = self.conn.add_stream(
            getattr, self.vessel, "available_thrust"
        )
        self.mass_stream = self.conn.add_stream(
            getattr, self.vessel, "mass"
        )
        self.throttle_stream = self.conn.add_stream(
            getattr, self.vessel.control, "throttle"
        )
        self.velocity_stream = self.conn.add_stream(
            getattr, self.flight, "velocity"
        )
        self.speed_stream = self.conn.add_stream(
            getattr, self.flight, "speed"
        )
        self.v_speed_stream = self.conn.add_stream(
            getattr, self.flight, "vertical_speed"
        )
        self.h_speed_stream = self.conn.add_stream(
            getattr, self.flight, "horizontal_speed"
        )
        self.height_stream = self.conn.add_stream(
            getattr, self.flight, "surface_altitude"
        )

    def __del__(self) -> None:
        self.thrust_stream.remove()
        self.mass_stream.remove()
        self.throttle_stream.remove()
        self.velocity_stream.remove()
        self.speed_stream.remove()
        self.v_speed_stream.remove()
        self.h_speed_stream.remove()
        self.height_stream.remove()


    def do(self) -> None:
        if self.thrust_stream() == 0:
            return

        # TODO discover why I add 5 here
        dist_center_to_bottom = self.get_distance_vessel_center_to_bottom() + 5
        safe_margin = dist_center_to_bottom + self.SAFE_MARGIN_OFFSET

        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.reference_frame = self.vessel.orbit.body.\
                                                 reference_frame

        self.set_direction_to_retrograde()
        self.vessel.control.speed_mode = spacecenter.SpeedMode.surface

        self.reduce_horizontal_speed()        

        self.vessel.control.throttle = 0
        self.vessel.control.speed_mode = spacecenter.SpeedMode.surface
        self.vessel.control.gear = True

        self.reduce_vertical_speed(dist_center_to_bottom, safe_margin)

        while self.height_stream() > dist_center_to_bottom:
            self.set_direction_to_retrograde()
            twr = self.get_twr()
            thrust_final_speed = 1 / twr
            self.vessel.control.throttle = thrust_final_speed

        self.vessel.control.throttle = 0
        self.vessel.auto_pilot.disengage()
        self.vessel.control.sas = True

    def get_twr(self) -> float:
        gravity = self.vessel.orbit.body.surface_gravity
        return self.thrust_stream() / (gravity * self.mass_stream())

    def reduce_horizontal_speed(self) -> None:
        while (self.h_speed_stream() > 10):
            self.set_direction_to_retrograde()

            height_sb = self.get_height_to_start_sb()
            if self.height_stream() > height_sb + self.OFFSET_TO_HORIZONTAL_SB:
                continue

            if self.throttle_stream() < 1:
                self.vessel.control.throttle = 1

    def reduce_vertical_speed(self, dist_center_to_bottom: float,
                              safe_margin: float) -> None:
        while self.speed_stream() > self.FINAL_SPEED:
            self.set_direction_to_retrograde()

            throttle = self.throttle_stream()
            height_sb = self.get_height_to_start_sb() + safe_margin
            if height_sb < self.height_stream() - dist_center_to_bottom:
                if throttle > 0:
                    self.vessel.control.throttle = 0
                continue

            if throttle < 1:
                self.vessel.control.throttle = 1

    def get_distance_vessel_center_to_bottom(self) -> float:
        refframe = self.vessel.reference_frame
        bbox = self.vessel.bounding_box(refframe)
        min_y = bbox[0][2]
        return abs(min_y)

    def set_direction_to_retrograde(self) -> None:
        velocity = self.velocity_stream()
        direction = (-velocity[0], -velocity[1], -velocity[2])
        self.vessel.auto_pilot.target_direction = direction

    def get_height_to_start_sb(self) -> float:
        twr = self.get_twr()
        gravity = self.vessel.orbit.body.surface_gravity
        current_speed = self.v_speed_stream()
        acceleration = twr * gravity - gravity
        time = current_speed / acceleration
        height = (current_speed / 2) * time
        return height
