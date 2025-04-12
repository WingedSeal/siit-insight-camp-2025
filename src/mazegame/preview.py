from math import floor
from typing import cast
import pygame
from pygame import locals

from .color import Color

from .direction import Direction
from .game import Game
from .map import Enemy, Map, SurfsType


_TEXT_COLOR = pygame.Color(255, 255, 255)
_TEXT_SHADOW_COLOR = pygame.Color(0, 0, 0)
_ARROW_PADDING = 0.3
_ARROW_WIDTH = 0.05
_ARROW_HEAD_HEIGHT = 0.1
_ARROW_HEAD_PADDING = 0.1
_ARROW_HEAD_WIDTH_OFFSET = 0.05
_CIRCLE_ARROW_HEAD_WIDTH_OFFSET = 0.1
_CIRCLE_OUTER_RADIUS = 0.175
_CIRCLE_INNER_RADIUS = 0.15
_CIRCLE_PADDING_LEFT = 0.2
_CIRCLE_PADDING_TOP = 0.1
_TIMES_PADDING_LEFT = 0.1
_TIMES_PADDING_TOP = 0.0


class ColorGenerator:
    _colors: list[Color]

    def reset_color(self):
        self._colors = Color.get_unique_colors(None)

    def __init__(self) -> None:
        self.reset_color()

    def get_color(self) -> pygame.Color:
        color = self._colors.pop()

        if not self._colors:
            self.reset_color()
        if color == Color.RED:
            return self.get_color()
        return color.value


def enemy_to_path_points(
    enemy: Enemy,
) -> list[tuple[float, float, float, float, Direction] | tuple[int, int, int]]:
    """
    Create list of path points to generate arrow

    :param enemy: Enenmy
    :return: List of either (tuple of start_pos.x, start_pos.y, end_pos.x, end_pos.y, direction) for move or (tuple of pos.x, pos.y, times) for halt
    """
    path = enemy.path
    starting_point = enemy.pos
    last_move = None
    last_move_count = 1
    condensed_path: list[tuple[Direction, int]] = []
    for move in path:
        if move != last_move:
            if last_move is not None:
                condensed_path.append((last_move, last_move_count))
                last_move_count = 1
            last_move = move
        else:
            last_move_count += 1
    if last_move is not None:
        condensed_path.append((last_move, last_move_count))
    path_points: list[
        tuple[float, float, float, float, Direction] | tuple[int, int, int]
    ] = []
    _path_points_tile: list[tuple[int, int]] = [starting_point]
    for direction, length in condensed_path:
        match direction:  # The arrow is on the left of the direction its facing ()
            case Direction.UP:
                new_path = (
                    _path_points_tile[-1][0] + _ARROW_PADDING,
                    _path_points_tile[-1][1] + 0.5,
                    _path_points_tile[-1][0] + _ARROW_PADDING,
                    _path_points_tile[-1][1] - length + 0.5,
                    direction,
                )
            case Direction.DOWN:
                new_path = (
                    _path_points_tile[-1][0] + 1 - _ARROW_PADDING,
                    _path_points_tile[-1][1] + 0.5,
                    _path_points_tile[-1][0] + 1 - _ARROW_PADDING,
                    _path_points_tile[-1][1] + length + 0.5,
                    direction,
                )
            case Direction.LEFT:
                new_path = (
                    _path_points_tile[-1][0] - 0.5,
                    _path_points_tile[-1][0] + _ARROW_PADDING,
                    _path_points_tile[-1][0] - length - 0.5,
                    _path_points_tile[-1][0] + _ARROW_PADDING,
                    direction,
                )
            case Direction.RIGHT:
                new_path = (
                    _path_points_tile[-1][0] - 0.5,
                    _path_points_tile[-1][0] + 1 - _ARROW_PADDING,
                    _path_points_tile[-1][0] + length - 0.5,
                    _path_points_tile[-1][0] + 1 - _ARROW_PADDING,
                    direction,
                )
            case Direction.HALT:
                new_path = (*_path_points_tile[-1], length)
        path_points.append(new_path)
        if not isinstance(new_path[0], int):
            new_path = cast(tuple[float, float, float, float, Direction], new_path)
            _path_points_tile.append((floor(new_path[2]), floor(new_path[3])))
    return path_points


class Preview:
    def __init__(self, map: Map) -> None:
        self.map = map
        self.surfs: SurfsType = {}
        self.tile_size, self.screen_width, self.screen_height = self._get_tile_size()
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont(
            "Times New Roman", self.tile_size // 5, bold=True
        )
        self.font_shadow = pygame.font.SysFont(
            "Times New Roman", self.tile_size // 4, bold=True
        )
        self.display_surface = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        self.surface_overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        self.color_generator = ColorGenerator()
        for y, row in enumerate(self.map.map):
            for x, tile in enumerate(row):
                if tile is None:
                    continue
                tile.init((x, y), self.tile_size, self.surfs)
                if tile.tile_under is not None:
                    tile.tile_under.init((x, y), self.tile_size, self.surfs)
                    tile.tile_under.rect.topleft = tile.tile_under.get_top_left((x, y))
                tile.rect.topleft = tile.get_top_left((x, y))
                if tile._auto_remove:
                    self.map.map[y][x] = tile.tile_under

    def _get_tile_size(self) -> tuple[int, int, int]:
        """
        Calculate tile size in pixel from map

        :return: Tuple of tile_size, screen_width, screen_height
        """
        max_width = Game.DEFAULT_WIDTH // self.map.width
        max_height = Game.DEFAULT_HEIGHT // self.map.height
        tile_size = min(max_width, max_height)
        screen_width = self.map.width * tile_size
        screen_height = self.map.height * tile_size
        return tile_size, screen_width, screen_height

    def teardown(self) -> None:
        pygame.quit()

    def draw_halt(
        self, pos: tuple[int, int], times: int, color: pygame.Color, index: int
    ) -> None:
        for font, text_color in (
            (self.font_shadow, _TEXT_SHADOW_COLOR),
            (self.font, color),
        ):
            self.surface_overlay.blit(
                font.render(f"x{times}", True, text_color),
                (
                    self.tile_size
                    * (
                        pos[0]
                        + _CIRCLE_PADDING_LEFT
                        + _CIRCLE_OUTER_RADIUS * 2
                        + _TIMES_PADDING_LEFT
                    ),
                    self.tile_size * (pos[1] + _TIMES_PADDING_TOP),
                ),
            )

        pygame.draw.circle(
            self.surface_overlay,
            color,
            (
                (pos[0] + _CIRCLE_PADDING_LEFT + _CIRCLE_OUTER_RADIUS) * self.tile_size,
                (pos[1] + _CIRCLE_PADDING_TOP) * self.tile_size,
            ),
            _CIRCLE_OUTER_RADIUS * self.tile_size,
        )
        pygame.draw.circle(
            self.surface_overlay,
            (0, 0, 0, 0),
            (
                (pos[0] + _CIRCLE_PADDING_LEFT + _CIRCLE_OUTER_RADIUS) * self.tile_size,
                (pos[1] + _CIRCLE_PADDING_TOP) * self.tile_size,
            ),
            _CIRCLE_INNER_RADIUS * self.tile_size,
        )
        pygame.draw.polygon(
            self.surface_overlay,
            color,
            [
                (
                    (
                        pos[0]
                        + _CIRCLE_PADDING_LEFT
                        + _CIRCLE_OUTER_RADIUS
                        + _ARROW_HEAD_HEIGHT
                    )
                    * self.tile_size,
                    (
                        pos[1]
                        + _CIRCLE_PADDING_TOP
                        + _CIRCLE_INNER_RADIUS
                        - _CIRCLE_ARROW_HEAD_WIDTH_OFFSET
                    )
                    * self.tile_size,
                ),
                (
                    (pos[0] + _CIRCLE_PADDING_LEFT + _CIRCLE_OUTER_RADIUS)
                    * self.tile_size,
                    (pos[1] + _CIRCLE_PADDING_TOP + _CIRCLE_INNER_RADIUS)
                    * self.tile_size,
                ),
                (
                    (
                        pos[0]
                        + _CIRCLE_PADDING_LEFT
                        + _CIRCLE_OUTER_RADIUS
                        + _ARROW_HEAD_HEIGHT
                    )
                    * self.tile_size,
                    (
                        pos[1]
                        + _CIRCLE_PADDING_TOP
                        + _CIRCLE_INNER_RADIUS
                        + _CIRCLE_ARROW_HEAD_WIDTH_OFFSET
                    )
                    * self.tile_size,
                ),
            ],
        )
        for font, text_color in (
            (self.font_shadow, _TEXT_SHADOW_COLOR),
            (self.font, _TEXT_COLOR),
        ):
            self.surface_overlay.blit(
                font.render(f"{index + 1}", True, text_color),
                (
                    self.tile_size
                    * (pos[0] + _CIRCLE_PADDING_LEFT + (_CIRCLE_INNER_RADIUS / 2)),
                    self.tile_size * (pos[1]),
                ),
            )

    def draw_arrow(
        self,
        start_pos: tuple[float, float],
        end_pos: tuple[float, float],
        direction: Direction,
        color: pygame.Color,
        index: int,
    ) -> None:
        left = min(start_pos[0], end_pos[0])
        top = min(start_pos[1], end_pos[1])
        match direction:
            case Direction.UP | Direction.DOWN:
                size_x = _ARROW_WIDTH
                size_y = (
                    abs(end_pos[1] - start_pos[1])
                    - _ARROW_HEAD_HEIGHT
                    - _ARROW_HEAD_PADDING
                )
                left -= _ARROW_WIDTH / 2
            case Direction.LEFT | Direction.RIGHT:
                size_x = (
                    abs(end_pos[0] - start_pos[0])
                    - _ARROW_HEAD_HEIGHT
                    - _ARROW_HEAD_PADDING
                )
                size_y = _ARROW_WIDTH
                top -= _ARROW_WIDTH / 2
            case Direction.HALT:
                raise ValueError("Cannot draw arrow for halt")
        match direction:
            case Direction.UP:
                top += _ARROW_HEAD_HEIGHT + _ARROW_HEAD_PADDING
            case Direction.LEFT:
                left += _ARROW_HEAD_HEIGHT + _ARROW_HEAD_PADDING
        arrow_points: list[tuple[float, float]]
        match direction:
            case Direction.UP:
                arrow_points = [
                    (left - _ARROW_HEAD_WIDTH_OFFSET, top),
                    (left + size_x / 2, top - _ARROW_HEAD_HEIGHT),
                    (left + size_x + _ARROW_HEAD_WIDTH_OFFSET, top),
                ]
            case Direction.DOWN:
                arrow_points = [
                    (left - _ARROW_HEAD_WIDTH_OFFSET, top + size_y),
                    (left + size_x / 2, top + size_y + _ARROW_HEAD_HEIGHT),
                    (left + size_x + _ARROW_HEAD_WIDTH_OFFSET, top + size_y),
                ]
            case Direction.LEFT:
                arrow_points = [
                    (left, top + size_y + _ARROW_HEAD_WIDTH_OFFSET),
                    (left - _ARROW_HEAD_HEIGHT, top + size_y / 2),
                    (left, top - _ARROW_HEAD_WIDTH_OFFSET),
                ]
            case Direction.RIGHT:
                arrow_points = [
                    (left + size_x, top + size_y + _ARROW_HEAD_WIDTH_OFFSET),
                    (left + size_x - _ARROW_HEAD_HEIGHT, top + size_y / 2),
                    (left + size_x, top - _ARROW_HEAD_WIDTH_OFFSET),
                ]

        arrow_points = [
            (arrow_point[0] * self.tile_size, arrow_point[1] * self.tile_size)
            for arrow_point in arrow_points
        ]
        self.display_surface.fill(
            color,
            (
                left * self.tile_size,
                top * self.tile_size,
                size_x * self.tile_size,
                size_y * self.tile_size,
            ),
        )
        pygame.draw.polygon(self.display_surface, color, arrow_points)
        for font, text_color in (
            (self.font_shadow, _TEXT_SHADOW_COLOR),
            (self.font, _TEXT_COLOR),
        ):
            self.surface_overlay.blit(
                font.render(f"{index + 1}", True, text_color),
                (
                    self.tile_size * (left),
                    self.tile_size * (top),
                ),
            )

    def run(self) -> None:
        self.display_surface.fill(Game.BG_COLOR)
        for row in self.map.map:
            for tile in row:
                if tile is None:
                    continue
                assert hasattr(tile, "surf")
                assert hasattr(tile, "rect")
                if tile.tile_under is not None:
                    self.display_surface.blit(
                        tile.tile_under.surf, tile.tile_under.rect
                    )
                self.display_surface.blit(tile.surf, tile.rect)
        enemies = self.map.get_tiles(Enemy)
        self.surface_overlay.fill((0, 0, 0, 0))
        for enemy in enemies:
            color = self.color_generator.get_color()
            path_points = enemy_to_path_points(enemy)
            for i, path_point in enumerate(path_points):
                if isinstance(path_point[0], int):
                    path_point = cast(tuple[int, int, int], path_point)
                    self.draw_halt(path_point[0:2], path_point[2], color, i)
                else:
                    path_point = cast(
                        tuple[float, float, float, float, Direction], path_point
                    )
                    self.draw_arrow(
                        path_point[0:2], path_point[2:4], path_point[4], color, i
                    )
            self.surface_overlay.blit(
                self.font.render(f"{enemy.chance_to_move:.0%}", True, _TEXT_COLOR),
                (
                    self.tile_size * (enemy.pos[0] + 0.1),
                    self.tile_size * (enemy.pos[1] + 0.3),
                ),
            )
        self.display_surface.blit(self.surface_overlay, self.surface_overlay.get_rect())
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == locals.QUIT:
                    self.teardown()
                    return
