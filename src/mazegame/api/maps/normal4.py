from ...direction import Direction
from ...color import Color
from ...map import CustomMapType, Door, Enemy, Exit, Key, Map, Block, Player, Lock


def _get_map():
    color1, color2 = Color.get_unique_colors(2)
    KEY1 = Key(color1)
    LOCK2 = Lock(color2)
    DOOR1 = Door(color1)
    DOOR2 = Door(color2, open=True)
    ENEMY1 = Enemy(
        [Direction.UP] * 5 + [Direction.DOWN] * 7 + [Direction.UP] * 2, boss=True
    )
    ENEMY2 = Enemy(
        [Direction.HALT] * 12
        + [Direction.DOWN]
        + [Direction.HALT] * 12
        + [Direction.UP]
    )
    # fmt: off
    NORMAL4_1 = Map(
        [
            [Block(), None,     Block(), None],
            [Block(), DOOR2,    Block(), None],
            [Block(), KEY1,     Block(), None],
            [Block(), None,     Block(), None],
            [Block(), None,     Block(), Exit()],
            [Block(), ENEMY1,   Block(), None],
            [Block(), LOCK2,    Block(), None],
            [Block(), Player(), ENEMY2,  DOOR1],
            [Block(), Block(),  None,    Block()]
        ]
    )
    # fmt: on
    return (
        [NORMAL4_1],
        """Enemy to your right will not move away in time, use that Lock wisely!""",
    )


NORMAL4: CustomMapType = _get_map

# def script():
#     for _ in range(5):
#         wait()
#     for _ in range(5):
#         move(UP)
#     for _ in range(5):
#         move(DOWN)
#     move(RIGHT)
#     move(RIGHT)
#     for _ in range(3):
#         move(UP)
