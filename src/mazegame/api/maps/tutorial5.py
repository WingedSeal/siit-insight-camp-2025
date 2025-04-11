from ...color import Color
from ...map import Block, Exit, Map, Player, Spike


TUTORIAL5 = Map(
    [
        [Block(), Exit(), Block(), Block(), None],
        [Block(), None, Block(), Spike(), None],
        [Block(), Player(), Block(), Player(), None],
    ]
)
