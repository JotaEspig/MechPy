from mechpy import mechpy


def main() -> None:
    mech = mechpy.MechPy()
    print(mech.conn.krpc.get_status().version)
    #mech.do_maneuver()
    #mech.launch_into_orbit(80000, 3000, 35000)
    mech.suicide_burn()


if __name__ == "__main__":
    main()
