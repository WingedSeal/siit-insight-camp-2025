import random

from ...color import Color
from ...map import (
    ColoredFloor,
    CustomMapType,
    Door,
    DoorFrame,
    Exit,
    Map,
    Block,
    Player,
    Spike,
    Lock,
)


def _get_map():
    color1, color2, color3, color4 = Color.get_unique_colors(4)
    NORMAL3_1 = Map(
        [
            [
                Exit(),
                Lock(color3),
                Door(color3, open=True),
                None,
                Door(color4, open=True),
                Lock(color4),
                Spike(),
            ],
            [
                Block(),
                Block(),
                Block(),
                ColoredFloor(color1),
                Block(),
                Block(),
                Block(),
            ],
            [Block(), Block(), Block(), None, Block(), Block(), Block()],
            [Block(), Block(), Block(), None, Block(), Block(), Block()],
            [
                Block(),
                Block(),
                Block(),
                ColoredFloor(color1),
                Block(),
                Block(),
                Block(),
            ],
            [Block(), Block(), Block(), Player(), Block(), Block(), Block()],
        ]
    )

    NORMAL3_2 = Map(
        [
            [
                Spike(),
                Lock(color3),
                Door(color3, open=True),
                None,
                Door(color4, open=True),
                Lock(color4),
                Exit(),
            ],
            [
                Block(),
                Block(),
                Block(),
                ColoredFloor(color2),
                Block(),
                Block(),
                Block(),
            ],
            [Block(), Block(), Block(), None, Block(), Block(), Block()],
            [Block(), Block(), Block(), None, Block(), Block(), Block()],
            [
                Block(),
                Block(),
                Block(),
                ColoredFloor(color1),
                Block(),
                Block(),
                Block(),
            ],
            [Block(), Block(), Block(), Player(), Block(), Block(), Block()],
        ]
    )

    return (
        [NORMAL3_1, NORMAL3_2],
        """If 2 colored floors have the same color, the exit will be on the left.
If 2 colored floors have different colors, the exit will be on the right.""",
    )


NORMAL3: CustomMapType = _get_map

# def script():
#     move(UP)
#     color = get_color()
#     for _ in range(3):
#         move(UP)
#     is_color_match = get_color() == color
#     move(UP)
#     for _ in range(3):
#         if is_color_match:
#             move(LEFT)
#         else:
#             move(RIGHT)
