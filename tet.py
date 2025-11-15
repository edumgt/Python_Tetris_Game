#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import random
import sys
from typing import Dict, List, Tuple, Optional

# ----------------------------------------------------
# 상수 정의
# ----------------------------------------------------
COLS = 10
ROWS = 20
CELL_SIZE = 30

PLAY_WIDTH = COLS * CELL_SIZE
PLAY_HEIGHT = ROWS * CELL_SIZE

WIN_WIDTH = 500
WIN_HEIGHT = 650

TOP_LEFT_X = (WIN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = 50

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (200, 30, 30)
GREEN = (30, 200, 30)
BLUE = (30, 30, 200)
YELLOW = (220, 220, 0)
CYAN = (0, 220, 220)
MAGENTA = (200, 0, 200)
ORANGE = (255, 165, 0)

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# ----------------------------------------------------
# 테트로미노 정의 (4x4 매트릭스)
# ----------------------------------------------------
SHAPES = [
    # I
    [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    # O
    [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    # T
    [[0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    # L
    [[1, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0]],
    # J
    [[0, 1, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0]],
    # S
    [[0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    # Z
    [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
]

# ----------------------------------------------------
# 보조 함수
# ----------------------------------------------------
def rotate_matrix(mat: List[List[int]]) -> List[List[int]]:
    """4x4 매트릭스를 시계 방향으로 90도 회전"""
    size = len(mat)
    return [[mat[size - 1 - x][y] for x in range(size)] for y in range(size)]


# ----------------------------------------------------
# Piece 클래스
# ----------------------------------------------------
class Piece:
    def __init__(self, x: int, y: int, shape_index: int):
        self.x = x
        self.y = y
        self.shape_index = shape_index
        self.matrix = [row[:] for row in SHAPES[shape_index]]
        self.color = COLORS[shape_index]

    def rotate(self) -> None:
        self.matrix = rotate_matrix(self.matrix)

    def get_positions(self) -> List[Tuple[int, int]]:
        """현재 위치 기준으로 실제 보드 좌표 반환"""
        positions = []
        for row in range(4):
            for col in range(4):
                if self.matrix[row][col] == 1:
                    positions.append((self.x + col, self.y + row))
        return positions

    def copy(self) -> 'Piece':
        """깊은 복사"""
        new_piece = Piece(self.x, self.y, self.shape_index)
        new_piece.matrix = [row[:] for row in self.matrix]
        return new_piece


# ----------------------------------------------------
# Board 클래스
# ----------------------------------------------------
class Board:
    def __init__(self):
        self.locked: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = self._create_grid()

    def _create_grid(self) -> List[List[Optional[Tuple[int, int, int]]]]:
        return [[self.locked.get((x, y)) for x in range(COLS)] for y in range(ROWS)]

    def update_grid(self) -> None:
        self.grid = self._create_grid()

    def is_valid_position(self, piece: Piece) -> bool:
        for x, y in piece.get_positions():
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and (x, y) in self.locked:
                return False
        return True

    def lock_piece(self, piece: Piece) -> None:
        for x, y in piece.get_positions():
            if y >= 0:
                self.locked[(x, y)] = piece.color
        self.update_grid()

    def clear_full_rows(self) -> int:
        cleared = 0
        for row in range(ROWS - 1, -1, -1):
            if all((col, row) in self.locked for col in range(COLS)):
                cleared += 1
                for col in range(COLS):
                    self.locked.pop((col, row), None)
                # 위 블록 내리기
                for y in range(row - 1, -1, -1):
                    for col in range(COLS):
                        key = (col, y)
                        if key in self.locked:
                            self.locked[(col, y + 1)] = self.locked.pop(key)
        self.update_grid()
        return cleared

    def is_game_over(self) -> bool:
        return any(y < 1 for (_, y) in self.locked.keys())


# ----------------------------------------------------
# TetrisGame 클래스 (메인 게임 로직)
# ----------------------------------------------------
class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption("Python Tetris")
        self.clock = pygame.time.Clock()

        self.board = Board()
        self.current_piece = self._get_new_piece()
        self.next_piece = self._get_new_piece()

        self.score = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 700  # ms
        self.game_over = False

        self.title_font = pygame.font.SysFont("malgungothic", 36, bold=True)
        self.info_font = pygame.font.SysFont("malgungothic", 20)
        self.game_over_font = pygame.font.SysFont("malgungothic", 32, bold=True)

    def _get_new_piece(self) -> Piece:
        index = random.randint(0, len(SHAPES) - 1)
        return Piece(COLS // 2 - 2, 0, index)

    def _update_level_and_speed(self) -> None:
        self.level = 1 + self.score // 500
        min_speed = 150
        self.fall_speed = max(700 - (self.level - 1) * 70, min_speed)

    def _try_move(self, dx: int, dy: int) -> bool:
        moved = self.current_piece.copy()
        moved.x += dx
        moved.y += dy
        if self.board.is_valid_position(moved):
            self.current_piece = moved
            return True
        return False

    def _try_rotate(self) -> bool:
        rotated = self.current_piece.copy()
        rotated.rotate()
        if self.board.is_valid_position(rotated):
            self.current_piece = rotated
            return True
        return False

    def _hard_drop(self) -> None:
        while self._try_move(0, 1):
            pass

    def _lock_current_piece(self) -> None:
        self.board.lock_piece(self.current_piece)
        cleared = self.board.clear_full_rows()
        if cleared > 0:
            self.score += (cleared ** 2) * 100
        self.current_piece = self.next_piece
        self.next_piece = self._get_new_piece()
        if not self.board.is_valid_position(self.current_piece):
            self.game_over = True

    def _draw_grid_lines(self) -> None:
        pygame.draw.rect(self.screen, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 2)
        for i in range(COLS + 1):
            x = TOP_LEFT_X + i * CELL_SIZE
            pygame.draw.line(self.screen, GRAY, (x, TOP_LEFT_Y), (x, TOP_LEFT_Y + PLAY_HEIGHT))
        for j in range(ROWS + 1):
            y = TOP_LEFT_Y + j * CELL_SIZE
            pygame.draw.line(self.screen, GRAY, (TOP_LEFT_X, y), (TOP_LEFT_X + PLAY_WIDTH, y))

    def _draw_board(self) -> None:
        for y in range(ROWS):
            for x in range(COLS):
                color = self.board.grid[y][x]
                if color:
                    pygame.draw.rect(
                        self.screen,
                        color,
                        (TOP_LEFT_X + x * CELL_SIZE, TOP_LEFT_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    )

    def _draw_piece(self, piece: Piece) -> None:
        for x, y in piece.get_positions():
            if y >= 0:
                pygame.draw.rect(
                    self.screen,
                    piece.color,
                    (TOP_LEFT_X + x * CELL_SIZE, TOP_LEFT_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )

    def _draw_next_piece(self) -> None:
        label = self.info_font.render("Next:", True, WHITE)
        self.screen.blit(label, (360, 100))

        start_x, start_y = 360, 130
        for row in range(4):
            for col in range(4):
                if self.next_piece.matrix[row][col] == 1:
                    pygame.draw.rect(
                        self.screen,
                        self.next_piece.color,
                        (start_x + col * CELL_SIZE, start_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    )
        pygame.draw.rect(self.screen, WHITE, (start_x - 5, start_y - 5, 4 * CELL_SIZE + 10, 4 * CELL_SIZE + 10), 1)

    def _draw_ui(self) -> None:
        self.screen.fill(BLACK)

        # 타이틀
        title = self.title_font.render("TETRIS", True, WHITE)
        self.screen.blit(title, (TOP_LEFT_X + PLAY_WIDTH // 2 - title.get_width() // 2, 5))

        # 점수 & 레벨
        score_text = self.info_font.render(f"Score : {self.score}", True, WHITE)
        level_text = self.info_font.render(f"Level : {self.level}", True, WHITE)
        self.screen.blit(score_text, (30, 100))
        self.screen.blit(level_text, (30, 130))

    def _draw_game_over(self) -> None:
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        text = self.game_over_font.render("GAME OVER", True, RED)
        score_text = self.info_font.render(f"Your Score : {self.score}", True, WHITE)
        info = self.info_font.render("Press ENTER to restart, ESC to quit", True, WHITE)

        self.screen.blit(text, (WIN_WIDTH // 2 - text.get_width() // 2, WIN_HEIGHT // 2 - 60))
        self.screen.blit(score_text, (WIN_WIDTH // 2 - score_text.get_width() // 2, WIN_HEIGHT // 2 - 20))
        self.screen.blit(info, (WIN_WIDTH // 2 - info.get_width() // 2, WIN_HEIGHT // 2 + 20))

    def reset(self) -> None:
        self.__init__()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(60)
            self.fall_time += dt
            self._update_level_and_speed()

            # 자동 낙하
            if not self.game_over and self.fall_time > self.fall_speed:
                self.fall_time = 0
                if not self._try_move(0, 1):
                    self._lock_current_piece()

            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if self.game_over:
                        if event.key == pygame.K_RETURN:
                            self.reset()
                        continue

                    if event.key == pygame.K_LEFT:
                        self._try_move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self._try_move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self._try_move(0, 1)
                    elif event.key == pygame.K_UP:
                        self._try_rotate()
                    elif event.key == pygame.K_SPACE:
                        self._hard_drop()

            # 그리기
            self._draw_ui()
            self._draw_board()
            self._draw_piece(self.current_piece)
            self._draw_grid_lines()
            self._draw_next_piece()

            if self.game_over:
                self._draw_game_over()

            pygame.display.update()

        pygame.quit()
        sys.exit()


# ----------------------------------------------------
# 실행
# ----------------------------------------------------
if __name__ == "__main__":
    TetrisGame().run()