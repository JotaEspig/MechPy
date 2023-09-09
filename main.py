from colorama import Fore
from colorama import just_fix_windows_console

from mechpy import mechpy


def maneuver(mech: mechpy.MechPy) -> None:
    mech.do_maneuver()

def launch_into_orbit(mech: mechpy.MechPy) -> None:
    target = int(input("Target altitude: "))
    start_turn = int(input("Gravitational turn start altitude: "))
    end_turn = int(input("Gravitational turn end altitude: "))
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
    print("=-=-=-=-= " + Fore.LIGHTGREEN_EX + "MENU" + Fore.RESET + " =-=-=-=-=")
    print(Fore.LIGHTRED_EX + "00" + Fore.RESET + " - Do maneuver")
    print(Fore.LIGHTRED_EX + "01" + Fore.RESET + " - Launch into orbit")
    print(Fore.LIGHTRED_EX + "02" + Fore.RESET + " - Suicide burn")
    print(Fore.LIGHTRED_EX + "99" + Fore.RESET + " - Exit")

# TODO make a UI ingame to do the choices instead of a CLI menu
def menu() -> None:
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
