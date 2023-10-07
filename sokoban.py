import keyboard
import copy
import os
import random
import threading
try:
    import msvcrt
except ImportError:
    import sys, termios

TITLE: str = "   ________  __ ______  ___  ___   _  __\n  / __/ __ \/ //_/ __ \/ _ )/ _ | / |/ /\n _\ \/ /_/ / ,< / /_/ / _  / __ |/    /\n/___/\____/_/|_|\____/____/_/ |_/_/|_/"
MIN_BOX_QUANTITY: int = 1
MIN_WIDTH: int = 3
MIN_HEIGHT: int = 3
BACKGROUND: str = '⬜️'
BARRIER: str = '🟦'
PLAYER: str = '🥵'
BOX: str = '📦'
DESTINATION: str = '🎯'
application_polling: bool = True
game_over: bool = False
width: int
height: int
player_coord: list[int]
box_coords: list[list[int]] = []
destination_coords: list[list[int]] = []
game_map: list[list[str]]
keys: set[str] = {'w', "up", 'a', "left", 's', "down", 'd', "right", 'r'}
is_released: dict[str, bool] = {key: True for key in keys}
box_quantity: int

def integer_input(prompt: str) -> int:
    integer_input: str = input(prompt)

    while not integer_input.isdigit():
        integer_input = input(prompt)

    return int(integer_input)

def flush_input() -> None:
    try:
        while msvcrt.kbhit():
            msvcrt.getch()
    except NameError:
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def reshuffle() -> None:
    global player_coord
    global box_coords
    global destination_coords

    available_coords: list[list[int]] = [[x, y] for y in range(height) for x in range(width)]
    random_coords: list[list[int]] = random.sample(available_coords, 1 + (box_quantity * 2))

    if len(box_coords) > 0:
        box_coords.clear()
    if len(destination_coords) > 0:
        box_coords.clear()

    player_coord = random_coords.pop(0)
    for _i in range(box_quantity):
        box_coords.append(random_coords.pop(0))
    destination_coords = random_coords

def render_map() -> None:
    renderer: list[list[str]] = copy.deepcopy(game_map)

    os.system("cls" if os.name == "nt" else "clear")

    renderer[player_coord[1]][player_coord[0]] = PLAYER
    for box_coord in box_coords:
        renderer[box_coord[1]][box_coord[0]] = BOX
    for destination_coord in destination_coords:
        if destination_coord not in box_coords:
            renderer[destination_coord[1]][destination_coord[0]] = DESTINATION
        else:
            renderer[destination_coord[1]][destination_coord[0]] = BARRIER
    renderer.insert(0, [BARRIER for _i in range(width)])
    renderer.insert(len(renderer), [BARRIER for _i in range(width)])
    for row in range(len(renderer)):
        renderer[row].insert(0, BARRIER)
        renderer[row].insert(len(renderer[row]), BARRIER)

    print(f"{TITLE}\n" + '\n'.join([''.join(row) for row in renderer]) + ("\nPress [R] to reshuffle the map.\nPress [Esc] to exit the game." if not is_game_over() else "\nPress [R] to restart the game.\nPress [Esc] to quit the game."))

def move_up() -> None:
    if player_coord[1] - 1 >= 0:
        if [player_coord[0], player_coord[1] - 1] in destination_coords:
            return
        elif [player_coord[0], player_coord[1] - 1] in box_coords:
            if player_coord[1] - 2 >= 0 and [player_coord[0], player_coord[1] - 2] in box_coords:
                return
            elif player_coord[1] - 2 < 0 and [player_coord[0], height - 1] in box_coords:
                return

        player_coord[1] -= 1
    elif player_coord[1] - 1 < 0:
        if [player_coord[0], height - 1] in destination_coords:
            return
        elif [player_coord[0], height - 1] in box_coords and [player_coord[0], height - 2] in box_coords:
            return

        player_coord[1] = height - 1
    if player_coord in box_coords:
        if player_coord[1] - 1 >= 0:
            box_coords[box_coords.index(player_coord)][1] -= 1
        elif player_coord[1] - 1 < 0:
            box_coords[box_coords.index(player_coord)][1] = height - 1

def move_left() -> None:
    if player_coord[0] - 1 >= 0:
        if [player_coord[0] - 1, player_coord[1]] in destination_coords:
            return
        elif [player_coord[0] - 1, player_coord[1]] in box_coords:
            if player_coord[0] - 2 >= 0 and [player_coord[0] - 2, player_coord[1]] in box_coords:
                return
            elif player_coord[0] - 2 < 0 and [width - 1, player_coord[1]] in box_coords:
                return

        player_coord[0] -= 1
    elif player_coord[0] - 1 < 0:
        if [width - 1, player_coord[1]] in destination_coords:
            return
        elif [width - 1, player_coord[1]] in box_coords and [width - 2, player_coord[1]] in box_coords:
            return

        player_coord[0] = width - 1
    if player_coord in box_coords:
        if player_coord[0] - 1 >= 0:
            box_coords[box_coords.index(player_coord)][0] -= 1
        elif player_coord[0] - 1 < 0:
            box_coords[box_coords.index(player_coord)][0] = width - 1

def move_down() -> None:
    if player_coord[1] + 1 < height:
        if [player_coord[0], player_coord[1] + 1] in destination_coords:
            return
        elif [player_coord[0], player_coord[1] + 1] in box_coords:
            if player_coord[1] + 2 < height and [player_coord[0], player_coord[1] + 2] in box_coords:
                return
            elif player_coord[1] + 2 >= height and [player_coord[0], 0] in box_coords:
                return

        player_coord[1] += 1
    elif player_coord[1] + 1 >= height:
        if [player_coord[0], 0] in destination_coords:
            return
        elif [player_coord[0], 0] in box_coords and [player_coord[0], 1] in box_coords:
            return

        player_coord[1] = 0
    if player_coord in box_coords:
        if player_coord[1] + 1 < height:
            box_coords[box_coords.index(player_coord)][1] += 1
        elif player_coord[1] + 1 >= height:
            box_coords[box_coords.index(player_coord)][1] = 0

def move_right() -> None:
    if player_coord[0] + 1 < width:
        if [player_coord[0] + 1, player_coord[1]] in destination_coords:
            return
        elif [player_coord[0] + 1, player_coord[1]] in box_coords:
            if player_coord[0] + 2 < width and [player_coord[0] + 2, player_coord[1]] in box_coords:
                return
            elif player_coord[0] + 2 >= width and [0, player_coord[1]] in box_coords:
                return

        player_coord[0] += 1
    elif player_coord[0] + 1 >= width:
        if [0, player_coord[1]] in destination_coords:
            return
        elif [0, player_coord[1]] in box_coords and [1, player_coord[1]] in box_coords:
            return

        player_coord[0] = 0
    if player_coord in box_coords:
        if player_coord[0] + 1 < width:
            box_coords[box_coords.index(player_coord)][0] += 1
        elif player_coord[0] + 1 >= width:
            box_coords[box_coords.index(player_coord)][0] = 0

def is_game_over() -> bool:
    for box_coord in box_coords:
        if box_coord not in destination_coords:
            return False
    return True

def exit_listener() -> None:
    global application_polling

    keyboard.wait("escape")
    application_polling = False
    os.system("cls" if os.name == "nt" else "clear")
    os._exit(1)

def start_game() -> None:
    global game_over
    global width
    global height
    global game_map
    global box_quantity

    os.system("cls" if os.name == "nt" else "clear")
    threading.Thread(target=exit_listener, args=()).start()

    while application_polling:
        game_over = False

        print(TITLE)

        box_quantity_input_prompt: str = f"Box quantity(Should not be less than {MIN_BOX_QUANTITY}): "
        box_quantity = integer_input(box_quantity_input_prompt)
        while box_quantity < MIN_BOX_QUANTITY:
            box_quantity = integer_input(box_quantity_input_prompt)

        map_width_input_prompt: str = f"Map's width(Should not be less than {MIN_WIDTH}): "
        width = integer_input(map_width_input_prompt)
        while width < MIN_WIDTH:
            width = integer_input(map_width_input_prompt)

        map_height_input_prompt = f"Map's height(Should not be less than {MIN_HEIGHT}): "
        height = integer_input(map_height_input_prompt)
        while height < MIN_HEIGHT:
            height = integer_input(map_height_input_prompt)

        while 1 + (box_quantity * 2) > width * height:
            width = integer_input("Pls provide a valid map width: ")
            height = integer_input("Pls provide a valid map height: ")

        game_map = [[BACKGROUND] * width for _i in range(height)]

        reshuffle()
        render_map()
        while not game_over:
            for key in keys:
                if is_released[key] and keyboard.is_pressed(key):
                    is_released[key] = False

                    if key in ['w', "up"]: move_up()
                    elif key in ['a', "left"]: move_left()
                    elif key in ['s', "down"]: move_down()
                    elif key in ['d', "right"]: move_right()
                    elif key == 'r': reshuffle()

                    render_map()

                    if is_game_over():
                        game_over = True
                        break
                elif not is_released[key] and not keyboard.is_pressed(key):
                    is_released[key] = True

        print("Game Over!")
        keyboard.wait('r')
        os.system("cls" if os.name == "nt" else "clear")
        flush_input()

if __name__ == "__main__":
    start_game()