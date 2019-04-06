import time
import curses
import asyncio
import random

TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)

        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)

        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)

        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)

        for _ in range(3):
            await asyncio.sleep(0)


def get_coordinates(row_range, column_range, count):
    coordinates = set()

    min_row, max_row = row_range
    min_column, max_column = column_range

    while len(coordinates) < count:
        row = random.randint(min_row, max_row)
        column = random.randint(min_column, max_column)

        if (row, column) not in coordinates:
            coordinates.add((row, column))

    return list(coordinates)


def draw(canvas):
    curses.curs_set(False)

    canvas.border()

    canvas_height, canvas_width = canvas.getmaxyx()

    stars_coordinates = get_coordinates(
        row_range=(1, canvas_height - 2),
        column_range=(1, canvas_width - 2),
        count=100,
    )

    coroutines = [
        blink(canvas, row, column, symbol=random.choice('*+.:'))
        for row, column in stars_coordinates
    ]

    while True:
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
