import asyncio
import curses
import random

from curses_tools import draw_frame, get_frame_size, read_controls


async def animate_gun_shot(
        canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_blinking_star(canvas, row, column, symbol='*'):
    current_frame = random.randint(1, 4)

    while True:
        if current_frame == 1:
            canvas.addstr(row, column, symbol, curses.A_DIM)

            for _ in range(20):
                await asyncio.sleep(0)

            current_frame = 2

        if current_frame == 2:
            canvas.addstr(row, column, symbol)

            for _ in range(3):
                await asyncio.sleep(0)

            current_frame = 3

        if current_frame == 3:
            canvas.addstr(row, column, symbol, curses.A_BOLD)

            for _ in range(5):
                await asyncio.sleep(0)

            current_frame = 4

        if current_frame == 4:
            canvas.addstr(row, column, symbol)

            for _ in range(3):
                await asyncio.sleep(0)

            current_frame = 1


async def animate_spaceship(
        canvas, start_row, start_column, frames, movement_speed=1):
    row, column = start_row, start_column

    canvas_height, canvas_width = canvas.getmaxyx()

    while True:
        for frame in frames:
            rows_direction, columns_direction, _ = read_controls(canvas)

            row += rows_direction * movement_speed
            column += columns_direction * movement_speed

            frame_height, frame_width = get_frame_size(frame)

            row = min(canvas_height - frame_height - 1, max(1, row))
            column = min(canvas_width - frame_width - 1, max(1, column))

            draw_frame(canvas, row, column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, negative=True)
