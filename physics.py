import math

from utils import limit


def _apply_acceleration(speed, speed_limit, forward=True):
    """Change speed — accelerate or brake — according to force direction."""

    speed_limit = abs(speed_limit)

    speed_fraction = speed / speed_limit

    # if the spaceship is standing still, then we accelerate quickly
    # if the spaceship is already flying fast, then we accelerate slowly
    delta = math.cos(speed_fraction) * 0.75

    result_speed = speed + delta if forward else speed - delta

    result_speed = limit(
        value=result_speed,
        min_value=-speed_limit,
        max_value=speed_limit,
    )

    # if the speed of the spaceship is close to zero, then we stop it
    if abs(result_speed) < 0.1:
        result_speed = 0

    return result_speed


def update_speed(row_speed, column_speed, rows_direction, columns_direction,
                 row_speed_limit=2, column_speed_limit=2, fading=0.8):
    """Update speed smootly to make control handy for player.

    Return new speed value (row_speed, column_speed)

    rows_direction — is a force direction by rows axis. Possible values:
       -1 — if force pulls up
       0  — if force has no effect
       1  — if force pulls down

    columns_direction — is a force direction by colums axis. Possible values:
       -1 — if force pulls left
       0  — if force has no effect
       1  — if force pulls right
    """

    if rows_direction not in (-1, 0, 1):
        raise ValueError(
            f'Wrong rows_direction value {rows_direction}. '
            f'Expects -1, 0 or 1.',
        )

    if columns_direction not in (-1, 0, 1):
        raise ValueError(
            f'Wrong columns_direction value {columns_direction}. '
            f'Expects -1, 0 or 1.',
        )

    if fading < 0 or fading > 1:
        raise ValueError(
            f'Wrong columns_direction value {fading}. '
            f'Expects float between 0 and 1.',
        )

    # reduce the speed so that the spaceship gradually stops
    row_speed *= fading
    column_speed *= fading

    row_speed_limit, column_speed_limit = (
        abs(row_speed_limit),
        abs(column_speed_limit),
    )

    if rows_direction != 0:
        row_speed = _apply_acceleration(
            speed=row_speed,
            speed_limit=row_speed_limit,
            forward=rows_direction > 0,
        )

    if columns_direction != 0:
        column_speed = _apply_acceleration(
            speed=column_speed,
            speed_limit=column_speed_limit,
            forward=columns_direction > 0,
        )
    return row_speed, column_speed
