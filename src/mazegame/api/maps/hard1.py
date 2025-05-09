from ...direction import Direction
from ...color import Color
from ...map import CustomMapType, Door, Enemy, Exit, Key, Map, Block, Player


def _get_map():
    ENEMY = Enemy(
        [Direction.UP] * 10 + [Direction.DOWN] * 10, chance_to_move=0.5, boss=True
    )

    HARD1_1 = Map(
        [
            [Block(), None, Exit(), Block()],
            [Block(), None, Block(), Block()],
            [Block(), None, Block(), Block()],
            [Block(), None, Block(), Block()],
            [Block(), None, Block(), Block()],
            [Block(), Door(Color.BLUE), Block(), Block()],
            [Block(), None, None, Block()],
            [Block(), None, Block(), Block()],
            [Block(), None, Block(), Block()],
            [Block(), Key(Color.BLUE), Block(), Block()],
            [Block(), ENEMY, Block(), Block()],
            [Block(), Player(), Block(), Block()],
        ]
    )

    return ([HARD1_1], "Don't forget that the enemy has a chance to not move.")


HARD1: CustomMapType = _get_map


# def script():
#     while get_tile(UP) == ENEMY:
#         move(HALT)
#     count = 0
#     while count < 5:
#         if get_tile(UP) == ENEMY:
#             move(HALT)
#         else:
#             move(UP)
#             count += 1
#     move(RIGHT)
#     while get_tile(LEFT) != ENEMY:
#         move(HALT)
#     while get_tile(LEFT) == ENEMY:
#         move(HALT)
#     move(LEFT)
#     for _ in range(6):
#         move(UP)
#     move(RIGHT)
