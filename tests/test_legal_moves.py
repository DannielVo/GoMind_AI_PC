import math

from bots.minimax_bot import HeuristicMinimaxBot
from core.board import Board, Player
from core.game import GameMode, GameSnapshot, GoGame


def make_ko_board():
    board = Board(5)
    for x, y in [(1, 0), (0, 1), (2, 1)]:
        board.set(x, y, Player.BLACK.value)
    for x, y in [(1, 1), (0, 2), (2, 2), (1, 3)]:
        board.set(x, y, Player.WHITE.value)
    return board


def test_empty_intersection_is_legal_and_original_unchanged():
    board = Board(5)
    next_board, captured = board.simulate_move(Player.BLACK, 2, 2)
    assert next_board is not None
    assert next_board.get(2, 2) == Player.BLACK.value
    assert board.get(2, 2) == 0
    assert captured == []


def test_occupied_and_out_of_bounds_moves_are_illegal():
    board = Board(5)
    board.set(2, 2, Player.BLACK.value)
    for x, y in [(2, 2), (-1, 2), (5, 2), (2, -1), (2, 5)]:
        next_board, captured = board.simulate_move(Player.WHITE, x, y)
        assert next_board is None
        assert captured == []


def test_suicide_is_illegal():
    board = Board(5)
    for x, y in [(1, 2), (2, 1), (3, 2), (2, 3)]:
        board.set(x, y, Player.BLACK.value)
    next_board, captured = board.simulate_move(Player.WHITE, 2, 2)
    assert next_board is None
    assert captured == []
    assert board.get(2, 2) == 0


def test_capture_with_no_initial_liberty_is_legal():
    board = make_ko_board()
    next_board, captured = board.simulate_move(Player.BLACK, 1, 2)
    assert next_board is not None
    assert set(captured) == {(1, 1)}
    assert next_board.get(1, 1) == 0
    assert next_board.get(1, 2) == Player.BLACK.value
    assert board.get(1, 1) == Player.WHITE.value


def test_simple_ko_rejects_immediate_recapture():
    before = make_ko_board()
    after, _ = before.simulate_move(Player.BLACK, 1, 2)
    assert after is not None
    recapture_without_ko, captured = after.simulate_move(Player.WHITE, 1, 1)
    assert recapture_without_ko is not None
    assert set(captured) == {(1, 2)}
    assert recapture_without_ko.grid == before.grid
    recapture_with_ko, _ = after.simulate_move(Player.WHITE, 1, 1, previous_board=before)
    assert recapture_with_ko is None


def test_game_legal_moves_and_apply_move_enforce_ko():
    before = make_ko_board()
    after, _ = before.simulate_move(Player.BLACK, 1, 2)
    assert after is not None
    game = GoGame(5, GameMode.HUMAN_VS_HUMAN)
    game.history = [
        GameSnapshot(before, Player.BLACK, 0, 0, None, 0),
        GameSnapshot(after, Player.WHITE, 1, 0, (1, 2), 0),
    ]
    game.current_index = 1
    game._load_snapshot(game.history[1])
    assert (1, 1) not in game.get_legal_moves(Player.WHITE)
    assert game._apply_move(Player.WHITE, 1, 1) is False
    assert game.board.grid == after.grid
    assert game.current_index == 1


def test_minimax_filters_ko_in_search():
    before = make_ko_board()
    after, _ = before.simulate_move(Player.BLACK, 1, 2)
    assert after is not None
    bot = HeuristicMinimaxBot(Player.WHITE, board_size=5, depth=2)
    moves = bot._generate_legal_moves(after, Player.WHITE, previous_board=before)
    assert (1, 1) not in moves


def test_minimax_candidates_are_legal_and_limited():
    board = Board(9)
    board.set(4, 4, Player.BLACK.value)
    bot = HeuristicMinimaxBot(Player.BLACK)
    moves = bot._generate_legal_moves(board, Player.BLACK)
    assert len(moves) <= 15
    assert len(moves) == len(set(moves))
    for x, y in moves:
        next_board, _ = board.simulate_move(Player.BLACK, x, y)
        assert next_board is not None


def test_minimax_returns_finite_score_without_candidates(monkeypatch):
    bot = HeuristicMinimaxBot(Player.BLACK)
    monkeypatch.setattr(bot, '_generate_legal_moves', lambda *args, **kwargs: [])
    score = bot._minimax(Board(9), 1, True, Player.BLACK, -math.inf, math.inf)
    assert math.isfinite(score)
