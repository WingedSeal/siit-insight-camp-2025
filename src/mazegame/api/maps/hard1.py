from ...direction import Direction
from ...color import Color
from ...map import ColoredFloor, Enemy, Map, Block, Player

ENEMY = Enemy(
    [Direction.UP] * 10 + [Direction.DOWN] * 10,
    chance_to_move=0.8,
)

HARD1 = Map(
    [
        [Block(), None, None, Block()],
        [Block(), None, Block(), Block()],
        [Block(), None, Block(), Block()],
        [Block(), None, Block(), Block()],
        [Block(), None, Block(), Block()],
        [Block(), None, Block(), Block()],
        [Block(), None, None, Block()],
        [Block(), None, Block(), Block()],
        [Block(), None, Block(), Block()],
        [Block(), None, Block(), Block()],
        [Block(), ENEMY, Block(), Block()],
        [Block(), Player(), Block(), Block()],
    ]
)

# def script():
#     while get_tile(UP) != ENEMY:
#         move(HALT)
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
#         move(LEFT)
#     for _ in range(6):
#         move(UP)
#     move(RIGHT)
