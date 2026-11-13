"""Stage 2: defensive candidate generation tests for GoMind AI PC."""

from bots.minimax_bot import HeuristicMinimaxBot
from core.board import Board, Player


def make_atari_board():
    """Black at (2,2) has exactly one liberty: (2,3)."""
    board = Board(5)
    board.set(2, 2, Player.BLACK.value)
    for x, y in [(1, 2), (2, 1), (3, 2)]:
        board.set(x, y, Player.WHITE.value)
    return board


def test_no_atari_groups_on_empty_board():
    board = Board(5)
    bot = HeuristicMinimaxBot(Player.BLACK, board_size=5)
    assert bot._find_atari_groups(board, Player.BLACK) == []
    assert bot._get_defensive_moves(board, Player.BLACK) == []


def test_detects_single_atari_group():
    board = make_atari_board()
    bot = HeuristicMinimaxBot(Player.BLACK, board_size=5)
    assert bot._find_atari_groups(board, Player.BLACK) == [{(2, 2)}]


def test_connected_stones_count_as_one_atari_group():
    board = Board(5)
    for x, y in [(2, 2), (2, 3)]:
        board.set(x, y, Player.BLACK.value)
    for x, y in [(1, 2), (3, 2), (2, 1), (1, 3), (3, 3)]:
        board.set(x, y, Player.WHITE.value)
    bot = HeuristicMinimaxBot(Player.BLACK, board_size=5)
    assert bot._find_atari_groups(board, Player.BLACK) == [{(2, 2), (2, 3)}]


def test_finds_escape_that_increases_liberties():
    board = make_atari_board()
    bot = HeuristicMinimaxBot(Player.BLACK, board_size=5)
    moves = bot._get_defensive_moves(board, Player.BLACK)
    assert (2, 3) in moves
    child, _ = board.simulate_move(Player.BLACK, 2, 3)
    assert child is not None
    assert bot._group_liberty(child, 2, 2) >= 2


def test_finds_capture_that_saves_atari_group():
    board = make_atari_board()
    for x, y in [(0, 2), (1, 1)]:
        board.set(x, y, Player.BLACK.value)
    bot = HeuristicMinimaxBot(Player.BLACK, board_size=5)
    moves = bot._get_defensive_moves(board, Player.BLACK)
    assert (1, 3) in moves
    child, captured = board.simulate_move(Player.BLACK, 1, 3)
    assert child is not None
    assert (1, 2) in captured
    assert bot._group_liberty(child, 2, 2) >= 2


def test_does_not_report_false_escape_when_group_remains_in_atari():
    board = make_atari_board()
    for x, y in [(1, 3), (3, 3)]:
        board.set(x, y, Player.WHITE.value)
    bot = HeuristicMinimaxBot(Player.BLACK, board_size=5)
    child, _ = board.simulate_move(Player.BLACK, 2, 3)
    assert child is not None
    assert bot._group_liberty(child, 2, 2) == 1
    assert (2, 3) not in bot._get_defensive_moves(board, Player.BLACK)


def test_defensive_move_survives_fifteen_candidate_limit():
    board = Board(9)
    for x, y in [(2, 2), (4, 2), (6, 2), (2, 4), (4, 4),
                 (6, 4), (2, 6), (4, 6), (6, 6), (7, 7)]:
        board.set(x, y, Player.BLACK.value)
    for x, y in [(6, 7), (7, 6), (8, 7)]:
        board.set(x, y, Player.WHITE.value)
    bot = HeuristicMinimaxBot(Player.BLACK, board_size=9)
    assert (7, 8) in bot._get_defensive_moves(board, Player.BLACK)
    moves = bot._generate_legal_moves(board, Player.BLACK)
    assert (7, 8) in moves
    assert len(moves) <= 15
    assert len(moves) == len(set(moves))


def test_defensive_moves_respect_previous_board_repetition_check():
    board = make_atari_board()
    bot = HeuristicMinimaxBot(Player.BLACK, board_size=5)
    previous_board, _ = board.simulate_move(Player.BLACK, 2, 3)
    assert previous_board is not None
    assert (2, 3) in bot._get_defensive_moves(board, Player.BLACK)
    assert (2, 3) not in bot._get_defensive_moves(
        board, Player.BLACK, previous_board=previous_board
    )
