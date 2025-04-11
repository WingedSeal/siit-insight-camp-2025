from abc import ABC, abstractmethod
import random
from typing import TYPE_CHECKING, Any, Type, TypeVar, override


import pygame


if TYPE_CHECKING:
    from .game import Game

from .direction import Direction
from .color import Color


def _lerp(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[int, int]:
    return (
        int((1 - t) * a[0] + t * b[0]),
        int((1 - t) * a[1] + t * b[1]),
    )


def _dash_lerp(
    a: tuple[float, float], b: tuple[float, float], t: float
) -> tuple[int, int]:
    return _lerp(a, b, 1 - (1 - t) ** 4)


class GetColor(ABC):
    @abstractmethod
    def get_color(self) -> Color:
        pass


class Tile(ABC, pygame.sprite.Sprite):
    surf: pygame.Surface
    tile_size = 0
    rect: pygame.Rect
    pos: tuple[int, int] = (0, 0)
    old_pos: tuple[int, int] = (0, 0)
    tile_under: "Tile | None" = None

    @abstractmethod
    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        pass

    def _pos_to_pixel(
        self, pos: tuple[int, int], padding: tuple[int, int] = (0, 0)
    ) -> tuple[int, int]:
        return (
            self.tile_size * pos[0] + padding[0],
            self.tile_size * pos[1] + padding[1],
        )

    def drop(self) -> None:
        pass

    def get_top_left(self, pos: tuple[int, int]) -> tuple[int, int]:
        return self._pos_to_pixel(pos)

    def animate(self, t: float):
        """
        Animate moving tile, default to dash lerp.

        :param start: start position
        :param end: end position
        :param t: time range between 0 and 1
        """
        pixel_pos = _dash_lerp(
            self.get_top_left(self.old_pos), self.get_top_left(self.pos), t
        )
        self.rect.topleft = pixel_pos

    def __eq__(self, value: object) -> bool:
        if type(self) == type(value):
            return True
        if isinstance(value, str):
            if self.__class__.__name__ == value:
                return True
        return False

    def __str__(self) -> str:
        return f"{self.__class__.__name__} at {self.pos}"

    # def __repr__(self) -> str:
    #     return str(self)


T = TypeVar("T", bound=Tile)


class TouchableTile(Tile):

    @abstractmethod
    def interacted_with(self, other_tile: Tile, game: "Game") -> None:
        pass


class Block(Tile):
    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if type(self) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size))
            self.surf.fill((255, 255, 0))
            surfs[type(self)] = self.surf
        else:
            self.surf = surfs[type(self)]
        self.rect = self.surf.get_rect()


class ColoredFloor(TouchableTile, GetColor):
    surfs: dict[Color, pygame.Surface] = {}

    def __init__(self, color: Color) -> None:
        self.color = color
        super().__init__()

    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if (type(self), self.color) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size))
            self.surf.fill(self.color.value)
            surfs[type(self), self.color] = self.surf
        else:
            self.surf = surfs[type(self), self.color]
        self.rect = self.surf.get_rect()

    def interacted_with(self, other_tile: Tile, game: "Game") -> None:
        pass

    def get_color(self) -> Color:
        return self.color

    def __str__(self) -> str:
        return f"{self.color} {self.__class__.__name__} at {self.pos}"


class ColoredBlock(Tile, GetColor):
    surfs: dict[Color, pygame.Surface] = {}

    def __init__(self, color: Color) -> None:
        self.color = color
        super().__init__()

    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if (type(self), self.color) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size))
            self.surf.fill(self.color.value)
            surfs[type(self), self.color] = self.surf
        else:
            self.surf = surfs[type(self), self.color]
        self.rect = self.surf.get_rect()

    def get_color(self) -> Color:
        return self.color

    def __str__(self) -> str:
        return f"{self.color} {self.__class__.__name__} at {self.pos}"


class Player(TouchableTile):
    index: int

    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if type(self) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            self.surf.fill(
                (255, 0, 0),
                (
                    tile_size * 0.05,
                    tile_size * 0.05,
                    tile_size * 0.90,
                    tile_size * 0.90,
                ),
            )
            surfs[type(self)] = self.surf
        else:
            self.surf = surfs[type(self)]
        self.rect = self.surf.get_rect()

    def interacted_with(self, other_tile: Tile, game: "Game") -> None:
        if not isinstance(other_tile, Enemy):
            return
        game.game_over(
            "Enemy ran into you.",
            random.choice(
                [
                    "That plan did not go well",
                    "Consider not dying, that's not a great plan",
                    '"Avoid collision" was a suggestion, apparently.',
                    "Dying isn't good for your health.",
                    "You have to be alive to win by the way.",
                ]
            ),
        )


class Door(Tile, GetColor):
    surfs: dict[Color, pygame.Surface] = {}

    def __init__(self, color: Color) -> None:
        self.color = color
        self.tile_under = DoorFrame(self)
        super().__init__()

    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if type(self) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            self.surf.fill(
                (100, 100, 100),
                (tile_size * 0.1, tile_size * 0.2, tile_size * 0.8, tile_size * 0.6),
            )
            surfs[type(self)] = self.surf
        else:
            self.surf = surfs[type(self)]
        self.rect = self.surf.get_rect()

    def get_color(self) -> Color:
        return self.color


class DoorFrame(TouchableTile, GetColor):
    surfs: dict[Color, pygame.Surface] = {}

    def __init__(self, door: Door) -> None:
        self.color = door.color
        self.door = door

    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if (type(self), self.color) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size))
            self.surf.fill(
                self.color.value,
                (0, 0, tile_size * 0.1, tile_size),
            )
            self.surf.fill(
                self.color.value,
                (tile_size * 0.9, 0, tile_size * 0.1, tile_size),
            )
            surfs[type(self), self.color] = self.surf
        else:
            self.surf = surfs[type(self), self.color]
        self.rect = self.surf.get_rect()

    def interacted_with(self, other_tile: Tile, game: "Game") -> None:
        pass

    def get_color(self) -> Color:
        return self.color


class Key(TouchableTile):
    surfs: dict[Color, pygame.Surface] = {}

    def __init__(self, color: Color) -> None:
        self.color = color
        super().__init__()

    def interacted_with(self, other_tile: Tile, game: "Game") -> None:
        if not isinstance(other_tile, Player):
            return
        other_tile.tile_under = None
        for y, row in enumerate(game.map.map):
            for x, tile in enumerate(row):
                if isinstance(tile, Door) and tile.color == self.color:
                    game.map.map[y][x] = tile.tile_under

    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if (type(self), self.color) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size))
            self.surf.fill(
                self.color.value,
                (tile_size * 0.45, tile_size * 0.45, tile_size * 0.1, tile_size * 0.1),
            )
            surfs[type(self), self.color] = self.surf
        else:
            self.surf = surfs[type(self), self.color]
        self.rect = self.surf.get_rect()


class Spike(TouchableTile):
    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if type(self) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size))
            self.surf.fill((255, 0, 255))
            surfs[type(self)] = self.surf
        else:
            self.surf = surfs[type(self)]
        self.rect = self.surf.get_rect()

    def interacted_with(self, other_tile: Tile, game: "Game") -> None:
        if not isinstance(other_tile, Player):
            return

        game.game_over(
            "You ran into a spike.",
            random.choice(
                [
                    "Did that spike not lsook dangerous.",
                    "It wasn't even moving.",
                    "Dying isn't good for your health.",
                    "Consider not doing that.",
                    "That's the spike!",
                ]
            ),
        )


class Exit(TouchableTile):
    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if type(self) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size))
            self.surf.fill((0, 255, 0))
            surfs[type(self)] = self.surf
        else:
            self.surf = surfs[type(self)]
        self.rect = self.surf.get_rect()

    def interacted_with(self, other_tile: Tile, game: "Game") -> None:
        if not isinstance(other_tile, Player):
            return

        game.game_won()


class Enemy(TouchableTile):
    def __init__(self, path: list[Direction], chance_to_move: float = 1.0) -> None:
        self.index = 0
        self.path = path
        self.chance_to_move = chance_to_move
        super().__init__()

    def init(
        self,
        pos: tuple[int, int],
        tile_size: int,
        surfs: dict[type["Tile"] | tuple[type["Tile"], Any], pygame.Surface],
    ) -> None:
        self.tile_size = tile_size
        self.pos = pos
        if type(self) not in surfs:
            self.surf = pygame.Surface((tile_size, tile_size))
            self.surf.fill((255, 0, 255))
            surfs[type(self)] = self.surf
        else:
            self.surf = surfs[type(self)]
        self.rect = self.surf.get_rect()

    def interacted_with(self, other_tile: Tile, game: "Game") -> None:
        if not isinstance(other_tile, Player):
            return

        game.game_over(
            "You ran into an enemy.",
            random.choice(
                [
                    "Stop touching people.",
                    "Invisibilty doesn't matter if you are running into them.",
                    "Dying isn't good for your health.",
                    "Consider not doing that.",
                    "They were just standing there. Why?",
                    "Avoid collisions!",
                    "Your enemies are not walls. Stop treating them as such.",
                ]
            ),
        )


class Map:
    def __init__(self, map: list[list[Tile | None]]) -> None:
        self.map = map
        self.height = len(map)
        self.width = len(map[0]) if map else 0
        for i, row in enumerate(map):
            if len(row) != self.width:
                raise ValueError(
                    f"Expected MxN matrix for map argument ({self.width}x{self.height}). Row {i} has different length ({len(row)})."
                )

    def get_positions(self, cls: Type[Tile]) -> list[tuple[int, int]]:
        """
        Find 1 or more positions of any tile type

        :return: tile position(s)
        """
        positions: list[tuple[int, int]] = []
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                if isinstance(tile, cls):
                    positions.append((x, y))
        return positions

    def get_tiles(self, cls: Type[T]) -> list[T]:
        """
        Find 1 or more tiles

        :return: tiles
        """
        tiles: list[T] = []
        for row in self.map:
            for tile in row:
                if isinstance(tile, cls):
                    tiles.append(tile)
        return tiles
