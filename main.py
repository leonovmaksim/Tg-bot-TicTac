from copy import deepcopy
import logging
import random
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TG_TOKEN')
if not TOKEN:
    raise ValueError("TG_TOKEN is not set in .env file!")
CONTINUE_GAME, FINISH_GAME = range(2)

FREE_SPACE = '.'
CROSS = 'X'
ZERO = 'O'

DEFAULT_STATE = [[FREE_SPACE for _ in range(3)] for _ in range(3)]


def get_default_state():
    return deepcopy(DEFAULT_STATE)


def generate_keyboard(state):
    """Генерация поля 3 на 3"""
    return [
        [InlineKeyboardButton(state[r][c],
                              callback_data=f'{r}{c}') for c in range(3)]
        for r in range(3)
    ]


def check_winner(state):
    for i in range(3):
        if state[i][0] == state[i][1] == state[i][2] != FREE_SPACE:
            return state[i][0]
        if state[0][i] == state[1][i] == state[2][i] != FREE_SPACE:
            return state[0][i]
    if state[0][0] == state[1][1] == state[2][2] != FREE_SPACE:
        return state[0][0]
    if state[0][2] == state[1][1] == state[2][0] != FREE_SPACE:
        return state[0][2]
    if all(cell != FREE_SPACE for row in state for cell in row):
        return 'ничья'
    return None


def make_random_move(state):
    free_positions = [(r, c) for r in range(3) for c in range(3)
                      if state[r][c] == FREE_SPACE]
    if free_positions:
        return random.choice(free_positions)
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['keyboard_state'] = get_default_state()
    context.user_data['current_turn'] = CROSS
    keyboard = generate_keyboard(context.user_data['keyboard_state'])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Ставь Х', reply_markup=reply_markup)
    return CONTINUE_GAME


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    position = query.data
    row, col = int(position[0]), int(position[1])
    state = context.user_data['keyboard_state']

    if state[row][col] != FREE_SPACE:
        await query.edit_message_text('Позиция занята, выбери другую.')
        return CONTINUE_GAME

    state[row][col] = CROSS
    winner = check_winner(state)

    if winner:
        await end_game(query, state, winner)
        return FINISH_GAME

    bot_move = make_random_move(state)
    if bot_move:
        bot_row, bot_col = bot_move
        state[bot_row][bot_col] = ZERO
        winner = check_winner(state)

        if winner:
            await end_game(query, state, winner)
            return FINISH_GAME

    keyboard = generate_keyboard(state)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Твоя очередь, ставь Х.',
                                  reply_markup=reply_markup)
    return CONTINUE_GAME


async def end_game(query, state, winner):
    keyboard = generate_keyboard(state)
    reply_markup = InlineKeyboardMarkup(keyboard)
    if winner == 'ничья':
        await query.edit_message_text('ничья!',
                                      reply_markup=reply_markup)
    else:
        await query.edit_message_text(f'{winner} выиграл',
                                      reply_markup=reply_markup)


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['keyboard_state'] = get_default_state()
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTINUE_GAME: [CallbackQueryHandler(game, pattern=r'^\d\d$')],
            FINISH_GAME: [CommandHandler('start', start)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
