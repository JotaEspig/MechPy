from mechpy import mechpy


def main() -> None:
    mech = mechpy.MechPy()
    print(mech.conn.krpc.get_status().version)
    print(mech.conn.space_center.active_vessel.auto_pilot.reference_frame)
    #mech.do_maneuver()
    mech.launch_into_orbit(20000, 4000, 8000)
    #mech.suicide_burn()


if __name__ == "__main__":
    main()
