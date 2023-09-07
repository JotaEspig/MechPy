from mechpy import mechpy


def main() -> None:
    mech = mechpy.MechPy()
    print(mech.conn.krpc.get_status().version)
    mech.do_maneuver()


if __name__ == "__main__":
    main()
