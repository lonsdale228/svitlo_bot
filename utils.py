import datetime
from typing import Tuple

import numpy as np
import pytz

from loader import TIMEZONE
from models import Zone

time = [f"0{i}:00:00" if i < 10 else f"{i}:00:00" for i in range(24)]

# TODO parsing data from web


def time_with_tz():
    return datetime.datetime.now(tz=pytz.timezone(TIMEZONE))


def time_format(seconds, is_striped=False) -> str:
    if seconds is not None:
        seconds = int(seconds)
        d = seconds // (3600 * 24)
        h = seconds // 3600 % 24
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60
        if is_striped:
            if d > 0:
                return '{:02d}:{:02d}:{:02d}:{:02d}'.format(d, h, m, s)
            elif h > 0:
                return '{:02d}:{:02d}:{:02d}'.format(h, m, s)
            elif m > 0:
                return '{:02d}:{:02d}'.format(m, s)
            elif s > 0:
                return '{:02d}'.format(s)
        else:
            if d > 0:
                return '{:02d} днів {:02d} годин {:02d} хвилин {:02d} сек'.format(d, h, m, s)
            elif h > 0:
                return '{:02d} годин {:02d} хвилин {:02d} секунд'.format(h, m, s)
            elif m > 0:
                return '{:02d} хвилин {:02d} сек'.format(m, s)
            elif s > 0:
                return '{:02d} сек'.format(s)
    return '-'


def get_next_item(arr, current_pos, shag=0):
    return np.take(arr, indices=current_pos + shag, mode='wrap')


def get_next_non_repeatable(arr, current_pos):
    itm = get_next_item(arr, current_pos)
    k = 0
    while itm == get_next_item(arr, current_pos, k):
        k += 1
    else:
        return get_next_item(arr, current_pos, k), current_pos + k


def get_time_by_pos(pos):
    return get_next_item(time, pos % len(time))


def time_left(t2, is_striped=True):
    t1 = datetime.datetime.strptime(time_with_tz().strftime("%H:%M:%S"), "%H:%M:%S")
    t2 = datetime.datetime.strptime(t2, "%H:%M:%S")
    return time_format(round((t2 - t1).total_seconds()), is_striped=is_striped)


def zone_to_string(zone: str) -> tuple[str, str]:
    match zone:
        case 'yes':
            return '<b>БІЛА ЗОНА</b>', '<b>БІЛОЇ ЗОНИ</b>'
        case 'no':
            return 'ЧОРНА ЗОНА', 'ЧОРНОЇ ЗОНИ'
        case 'maybe':
            return 'СІРА ЗОНА', 'СІРОЇ ЗОНИ'


def get_next_zones(zones: list, current_cell, num_zones: int = 5, ignore_not_black: bool = True):
    l = []
    index = current_cell
    for _ in range(num_zones):
        item, index = get_next_non_repeatable(zones, index)
        l.append(Zone(
            item,
            index,
            get_time_by_pos(index),
            time_left(get_time_by_pos(index)),
            zone_to_string(item)
        ))
    return l
