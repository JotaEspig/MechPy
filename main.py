import time

from colorama import Fore
from colorama import just_fix_windows_console

from mechpy import mechpy
from mechpy import displayer


def reset_display(mech: mechpy.MechPy) -> None:
    del mech.display


def maneuver(mech: mechpy.MechPy) -> None:
    mech.do_maneuver()


def launch_into_orbit(mech: mechpy.MechPy) -> None:
    size = mech.display.rect.size
    pos = mech.display.rect.position
    display = displayer.Displayer(
        mech.conn, size, (pos[0], pos[1] - size[1])
    )

    display.add_text("Target altitude:", (-65, 70))
    display.add_text("Turn start altitude:", (-65, 20))
    display.add_text("Turn end altitude:", (-65, -30))

    target_input_idx = display.add_input_field((-65, 50))
    start_turn_input_idx = display.add_input_field((-65, 0))
    end_turn_input_idx = display.add_input_field((-65, -50))

    button_idx = display.add_button("Go!", (0, -80))
    button_stream = display.get_button_clicked_stream(button_idx)
    while button_stream() == False:
        time.sleep(0.1)

    target = int(display.input_fields[target_input_idx].value)
    start_turn = int(display.input_fields[start_turn_input_idx].value)
    end_turn = int(display.input_fields[end_turn_input_idx].value)

    mech.launch_into_orbit(target, start_turn, end_turn)


def suicide_burn(mech: mechpy.MechPy) -> None:
    if mech.suicide_burn():
        print("The active vessel has 0 of thrust")


def mech_exit(mech: mechpy.MechPy) -> None:
    del mech
    exit()


FUNCTIONS = {
    0: maneuver,
    1: launch_into_orbit,
    2: suicide_burn,
    99: mech_exit,
}


def print_menu() -> None:
    print("=-=-=-=-= " + Fore.LIGHTGREEN_EX +
          "MENU" + Fore.RESET + " =-=-=-=-=")
    print(Fore.LIGHTRED_EX + "00" + Fore.RESET + " - Do maneuver")
    print(Fore.LIGHTRED_EX + "01" + Fore.RESET + " - Launch into orbit")
    print(Fore.LIGHTRED_EX + "02" + Fore.RESET + " - Suicide burn")
    print(Fore.LIGHTRED_EX + "99" + Fore.RESET + " - Exit")


def menu() -> None:
    # TODO make a UI ingame to do the choices instead of a CLI menu
    mech = mechpy.MechPy()
    print_menu()

    choice = int(input("Type your choice: "))
    fn = FUNCTIONS[choice]
    fn(mech)


def main() -> None:
    just_fix_windows_console()
    menu()


if __name__ == "__main__":
    main()
