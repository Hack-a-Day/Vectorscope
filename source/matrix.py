import vectoros
import asyncio
import keyleds
import keyboardcb
import timer
from vos_state import vos_state
import random

task_name = 'matrix'
_freeze = False
_exit = False
_menu_key = None

# Define a set of symbols to use in the Matrix effect
#symbols = ['カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト']
symbols = ['@', '#', '$', '%', '&', '*', '+', '=', '-', ';', ':', '|', '~', '?', '/']

def exit(key=None):
    global _exit
    _exit = True
    vectoros.remove_task(task_name)
    if _menu_key:
        _menu_key.detach()
    vos_state.show_menu = True
    print("Exit called, stopping task...")

def freeze(state=True):
    global _freeze
    _freeze = state
    print("Freeze state changed to:", state)

async def matrix_effect():
    global _exit
    screen = vectoros.get_screen()
    width, height = 240, 240
    column_width = 5
    num_columns = width // column_width
    columns = [height + 1] * num_columns

    while not _exit:
        screen.clear(0)  # Clear the screen for each new frame

        for i in range(num_columns):
            if columns[i] > height:
                if random.random() > 0.975:
                    columns[i] = 0
            else:
                columns[i] += 10

            symbol = random.choice(symbols)
            if columns[i] < height:
                screen.text(i * column_width, columns[i], symbol)

        await asyncio.sleep_ms(50)

async def vos_main():
    global _freeze, _exit, task_name, _menu_key
    _freeze = False
    _exit = False
    _menu_key = keyboardcb.KeyboardCB({keyleds.KEY_MENU: exit})
    if not vectoros.vectoros_active():
        keyboardcb.KeyboardCB.run(250)
        timer.Timer.run()
    await matrix_effect()

def main():
    asyncio.run(vos_main())

if __name__ == '__main__':
    vectoros.run()
