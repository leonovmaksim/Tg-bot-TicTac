import pytest
from copy import deepcopy
from main import get_default_state, check_winner, make_random_move

FREE_SPACE = '.'
CROSS = 'X'
ZERO = 'O'
DEFAULT_STATE = [[FREE_SPACE for _ in range(3)] for _ in range(3)]


@pytest.fixture
def empty_state():
    return deepcopy(DEFAULT_STATE)


@pytest.fixture
def winning_state_row():
    state = deepcopy(DEFAULT_STATE)
    state[0] = [CROSS, CROSS, CROSS]
    return state


@pytest.fixture
def winning_state_column():
    state = deepcopy(DEFAULT_STATE)
    for i in range(3):
        state[i][0] = ZERO
    return state


@pytest.fixture
def winning_state_diagonal():
    state = deepcopy(DEFAULT_STATE)
    for i in range(3):
        state[i][i] = CROSS
    return state


@pytest.fixture
def draw_state():
    return [
        [CROSS, ZERO, CROSS],
        [ZERO, CROSS, ZERO],
        [ZERO, CROSS, ZERO]
    ]


def test_get_default_state():
    state = get_default_state()
    assert state == DEFAULT_STATE, \
        "Изначальное состояние должно быть 3x3 сеткой с пустыми ячейками"


def test_check_winner_row(winning_state_row):
    winner = check_winner(winning_state_row)
    assert winner == CROSS, \
        "Победителем должен быть X при строке из иксов в ряд"


def test_check_winner_column(winning_state_column):
    winner = check_winner(winning_state_column)
    assert winner == ZERO, \
        "Победителем должен быть O при столбце из нулей"


def test_check_winner_diagonal(winning_state_diagonal):
    winner = check_winner(winning_state_diagonal)
    assert winner == CROSS, \
        "Победителем должен быть X при диагонали из иксов"


def test_check_winner_draw(draw_state):
    winner = check_winner(draw_state)
    assert winner == 'ничья', "Игра должна закончиться вничью."


def test_check_winner_no_winner(empty_state):
    winner = check_winner(empty_state)
    assert winner is None, \
        "Не должно быть победителя для пустой доски"


def test_make_random_move(empty_state):
    move = make_random_move(empty_state)
    assert move in [(r, c) for r in range(3) for c in range(3)], \
        "Случайный ход должен вернуть позицию из списка допустимых"
    row, col = move
    empty_state[row][col] = CROSS
    assert empty_state[row][col] == CROSS, \
        "Случайный ход должен правильно отмечать позицию"


def test_make_random_move_no_moves():
    full_state = [[CROSS for _ in range(3)] for _ in range(3)]
    move = make_random_move(full_state)
    assert move is None, \
        "Случ.ход должен вернуть None, если нет возможных ходов"
