import random
import sys
import threading
from typing import TYPE_CHECKING
import pygame
from pygame import locals

from .direction import Direction
from .map import Enemy, Map, Player, Tile, TouchableTile
from .control import Control


class Game:
    clock = pygame.time.Clock()
    DEFAULT_WIDTH = 1280
    DEFAULT_HEIGHT = 720
    MAX_FPS = 120
    MSPT = 500
    """Millisecond per tick"""
    TITLE = "Maze Game"
    BG_COLOR = pygame.Color(10, 10, 10)
    game_event = threading.Event()
    next_moves: list[tuple[int, int, int, int]] = []
    """Moves set by Control (pos_x, pos_y, dx, dy)"""
    is_control_alive = True

    def __init__(self, map: Map) -> None:
        self.control = Control(map, self)
        self.enemies = map.get_tiles(Enemy)
        self.players = map.get_tiles(Player)
        for i, player in enumerate(self.players):
            player.index = i
        self.game_event.set()
        pygame.init()
        self.map = map
        self.tile_size, self.screen_width, self.screen_height = self._get_tile_size()
        self.display_surface = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption(self.TITLE)
        self.delta_ms = 0.0
        self.tick_delta_ms = 0.0
        self.moving_tiles: list[Tile] = []
        """Time delta in milisecond"""
        for y, row in enumerate(self.map.map):
            for x, tile in enumerate(row):
                if tile is not None:
                    tile.init((x, y), self.tile_size)

    def _get_tile_size(self) -> tuple[int, int, int]:
        """
        Calculate tile size in pixel from map

        :return: Tuple of tile_size, screen_width, screen_height
        """
        max_width = self.DEFAULT_WIDTH // self.map.width
        max_height = self.DEFAULT_HEIGHT // self.map.height
        tile_size = min(max_width, max_height)
        screen_width = self.map.width * tile_size
        screen_height = self.map.height * tile_size
        return tile_size, screen_width, screen_height

    def teardown(self) -> None:
        pygame.quit()
        sys.exit()

    def _get_tile(self, x: int, y: int) -> Tile | None:
        if x < 0 or x >= self.map.width:
            return None
        if y < 0 or y >= self.map.height:
            return None
        return self.map.map[y][x]

    def get_tile(self, direction: Direction, player_index: int = 0) -> Tile | None:
        player = self.players[player_index]
        tile = self._get_tile(
            player.pos[0] + direction.value[0], player.pos[1] + direction.value[1]
        )
        return tile

    def run(self) -> None:
        """
        Starts game loop
        """
        while True:
            if self.update():
                break
        sys.exit()

    def tick(self) -> None:
        for tile in self.moving_tiles:
            tile.animate(1)
        self.moving_tiles = []

        if self.is_control_alive:
            self.game_event.clear()
            self.control.control_event.set()
            self.game_event.wait()
            for pos_x, pos_y, dx, dy in self.next_moves:
                if self.try_move_tile(pos_x, pos_y, dx, dy):
                    self.control.player_positions.append((pos_x + dx, pos_y + dy))
                else:
                    self.control.player_positions.append((pos_x, pos_y))
            self.next_moves = []

        for enemy in self.enemies:
            if random.random() >= enemy.chance_to_move:
                continue
            self.try_move_tile(
                enemy.pos[0],
                enemy.pos[1],
                enemy.path[enemy.index].value[0],
                enemy.path[enemy.index].value[1],
            )
            enemy.index = (enemy.index + 1) % len(enemy.path)

    def update(self) -> bool:
        """
        The game logic that occurs within a frame.

        :return: Whether the game should end
        """

        for event in pygame.event.get():
            if event.type == locals.QUIT:
                self.teardown()
                return True

        self.display_surface.fill(self.BG_COLOR)

        if self.tick_delta_ms > self.MSPT:
            self.tick_delta_ms -= self.MSPT
            self.tick()

        t = self.tick_delta_ms / self.MSPT
        for tile in self.moving_tiles:
            tile.animate(t)

        for row in self.map.map:
            for tile in row:
                if tile is None:
                    continue
                assert hasattr(tile, "surf")
                assert hasattr(tile, "rect")
                self.display_surface.blit(tile.surf, tile.rect)

        pygame.display.update()
        self.time_delta = self.clock.tick(self.MAX_FPS)
        self.tick_delta_ms += self.time_delta
        return False

    def try_move_tile(self, x: int, y: int, dx: int, dy: int) -> bool:
        """
        Try to move a tile, can fail

        :param x: Original Tile's x
        :param y: Original Tile's y
        :param dx: Target Tile's x
        :param dy: Target TIle's y
        :return: Whether it was successful
        """
        if y + dy >= self.map.height:
            return False
        if x + dx >= self.map.width:
            return False
        target = self.map.map[y + dy][x + dx]
        if target is not None and not isinstance(target, TouchableTile):
            return False
        tile = self.map.map[y][x]
        if tile is None:
            return False
        tile.old_pos = tile.pos
        tile.pos = (x + dx, y + dy)
        self.map.map[y + dy][x + dx] = tile
        self.map.map[y][x] = None
        self.moving_tiles.append(tile)
        if isinstance(target, TouchableTile):
            target.interact(tile)
        return True

    def render_map(self) -> None:
        pass
