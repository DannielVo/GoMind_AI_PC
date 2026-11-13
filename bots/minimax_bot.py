from __future__ import annotations
import math
import random
from typing import List, Tuple
from core.board import Board, Player


class HeuristicMinimaxBot:
    def __init__(self, color: Player, board_size: int = 9, depth: int | None = None):
        self.color = color
        self.board_size = board_size
        self.depth = depth if depth is not None else 2
        self.resign_threshold = -30.0

    def select_move(
        self,
        board: Board,
        legal_moves: List[Tuple[int, int]],
        previous_board: Board | None = None,
    ) -> Tuple[int, int] | str | None:

        if not legal_moves:
            return None

        best_score = -math.inf
        best_moves: List[Tuple[int, int]] = []

        for x, y in legal_moves:
            child, _ = board.simulate_move(
                self.color,
                x,
                y,
                previous_board,
            )

            if child is None:
                continue

            score = self._minimax(
                board=child,
                depth=max(0, self.depth - 1),
                maximizing=False,
                max_player=self.color,
                alpha=-math.inf,
                beta=math.inf,
                previous_board=board,
            )

            if score > best_score + 1e-6:
                best_score = score
                best_moves = [(x, y)]

            elif abs(score - best_score) <= 1e-6:
                best_moves.append((x, y))

        if not best_moves:
            return None

        if best_score < self.resign_threshold:
            return "RESIGN"

        return random.choice(best_moves)


    # ======================
    # MINIMAX + ALPHA-BETA
    # ======================

    def _minimax(
        self,
        board: Board,
        depth: int,
        maximizing: bool,
        max_player: Player,
        alpha: float,
        beta: float,
        previous_board: Board | None = None,
    ) -> float:

        if depth <= 0:
            return self._evaluate(board, max_player)

        current_player = (
            max_player if maximizing
            else max_player.opposite
        )

        legal_moves = self._generate_legal_moves(
            board,
            current_player,
            previous_board,
        )

        if not legal_moves:
            return self._evaluate(board, max_player)

        value = -math.inf if maximizing else math.inf
        explored = False

        for x, y in legal_moves:
            child, _ = board.simulate_move(
                current_player,
                x,
                y,
                previous_board,
            )

            if child is None:
                continue

            explored = True

            score = self._minimax(
                board=child,
                depth=depth - 1,
                maximizing=not maximizing,
                max_player=max_player,
                alpha=alpha,
                beta=beta,
                previous_board=board,
            )

            if maximizing:
                value = max(value, score)
                alpha = max(alpha, value)
            else:
                value = min(value, score)
                beta = min(beta, value)

            if beta <= alpha:
                break

        if not explored:
            return self._evaluate(board, max_player)

        return value

    # ======================
    # MOVE GENERATION
    # ======================

    def _generate_legal_moves(
        self,
        board: Board,
        player: Player,
        previous_board: Board | None = None,
    ) -> List[Tuple[int, int]]:
        size = board.size
        moves = []

        for y in range(size):
            for x in range(size):
                if board.get(x, y) != 0:
                    continue

                # ưu tiên ô gần quân mình
                for nx, ny in board._neighbors(x, y):
                    if board.get(nx, ny) == player.value:
                        moves.append((x, y))
                        break

        if len(moves) < 12:
            moves = [(x, y) for y in range(size) for x in range(size) if board.get(x, y) == 0]

        def move_priority(move):
            x, y = move
            score = 0

            # Ưu tiên ăn quân / gây atari
            for nx, ny in board._neighbors(x, y):
                if board.get(nx, ny) == player.opposite.value:
                    libs = self._group_liberty(board, nx, ny)
                    if libs == 1:
                        score += 100
                    elif libs == 2:
                        score += 20

            # Ưu tiên trung tâm nhẹ
            score += 4 - abs(4 - x) - abs(4 - y)
            return -score

        moves.sort(key=move_priority)

        legal_moves = []

        for x, y in moves:
            next_board, _ = board.simulate_move(
                player,
                x,
                y,
                previous_board,
            )

            if next_board is None:
                continue

            legal_moves.append((x, y))

            if len(legal_moves) >= 15:
                break

        return legal_moves

    # ======================
    # HEURISTIC EVALUATION
    # ======================

    def _evaluate(self, board: Board, max_player: Player) -> float:
        size = board.size
        opp = max_player.opposite

        stone_diff = 0
        territory_diff = 0
        capture_bonus = 0
        group_penalty = 0

        visited = set()

        for y in range(size):
            for x in range(size):
                v = board.get(x, y)

                if v == 0:
                    neighbor_colors = set()
                    for nx, ny in board._neighbors(x, y):
                        nv = board.get(nx, ny)
                        if nv != 0:
                            neighbor_colors.add(nv)
                    if len(neighbor_colors) == 1:
                        if max_player.value in neighbor_colors:
                            territory_diff += 1
                        else:
                            territory_diff -= 1
                    continue

                if v == max_player.value:
                    stone_diff += 1
                else:
                    stone_diff -= 1

                if (x, y) in visited:
                    continue

                libs, group = self._group_liberty_and_group(board, x, y)
                visited |= group

                if v == max_player.value:
                    if libs == 1:
                        group_penalty -= 8
                else:
                    if libs == 1:
                        capture_bonus += 8

        return (
            1.5 * stone_diff
            + 0.6 * territory_diff
            + capture_bonus
            + group_penalty
        )

    # ======================
    # GROUP / LIBERTY UTILS
    # ======================

    def _group_liberty(self, board: Board, x: int, y: int) -> int:
        libs, _ = self._group_liberty_and_group(board, x, y)
        return libs

    def _group_liberty_and_group(self, board: Board, x: int, y: int):
        color = board.get(x, y)
        stack = [(x, y)]
        visited = set()
        liberties = set()

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))

            for nx, ny in board._neighbors(cx, cy):
                v = board.get(nx, ny)
                if v == 0:
                    liberties.add((nx, ny))
                elif v == color:
                    stack.append((nx, ny))

        return len(liberties), visited
