from calendar import monthrange
from datetime import date, datetime, timedelta

from aiogram import types
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, bold

from bot_function.billing_class import BillingFunction
from create_bot import dp
from database.requests_class import RequestsFunction
from project.log_lib import get_logger
from utils.utils_functions import reg_expr, open_req_to_string

billing = BillingFunction()
requests = RequestsFunction()
logger = get_logger('logs')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    Sends a welcome/start message
    :param message: message from telegram chat
    """
    await message.answer("Привет! Я бот-помощник для интернет-провайдера.")


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    """
    Sends a help message
    :param message: message from telegram chat
    """
    msg = text(bold('Я могу ответить на следующие команды:'),
               '/report', '/reportmonth', '/add', '/close', '/set', '/check', sep='\n')
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['report'])
async def report_billing(message: types.Message):
    """
    Sends a daily report
    :param message: message from telegram chat
    """
    received_message = message.get_args().split(' ')
    default_date = [date.today() - timedelta(days=1)]

    try:
        received_date = [datetime.strptime(d, '%Y-%m-%d').date() for d in received_message]
    except ValueError:
        received_date = received_message

    date_bill = received_date if any(received_message) else default_date

    if len(date_bill) == 1:
        date_bill = {'first_date': date_bill[0], 'last_date': date_bill[0]}
    else:
        date_bill = {'first_date': date_bill[0], 'last_date': date_bill[1]}

    report = billing.billing_report(date_bill)
    await message.reply(report)


@dp.message_handler(commands=['reportmonth'])
async def accountants_report(message: types.Message):
    """
    Sends a monthly report
    :param message: message from telegram chat
    """
    prev_month = date.today().month - 1

    max_day = monthrange(date.today().year, prev_month)[1]
    prev_month = f'0{prev_month}' if prev_month < 10 else prev_month
    date_bill = {'first_date': date.fromisoformat(f'2022-{prev_month}-01'),
                 'last_date': date.fromisoformat(f'2022-{prev_month}-{max_day}')}
    report_month = billing.report_acc_bill(date_bill)
    await message.reply(report_month)


@dp.message_handler(commands=['activeUser'])
async def active_user(message: types.Message):
    """
    Runs script of updating table with active user
    :param message: message from telegram chat
    """
    billing.receive_user_data()
    await message.reply('Таблица с пользователя была обновлена')


@dp.message_handler(commands=['add'])
async def add_request(message: types.Message):
    """
    Runs script of adding a new repair request
    :param message: message from telegram chat
    """
    request = message.get_args()
    requests.add_request(request)

    logger.info('Adding request has been processed')
    await message.reply(f'Заявка "{request}" добавлена')


@dp.message_handler(commands=['close'])
async def closure_request(message: types.Message):
    """
    Prepares arguments and runs script of closing a repair request
    :param message: message from telegram chat
    """
    id_ = message.get_args()

    if id_.isdigit() and requests.check_existence_of_id(int(id_)):
        dict_of_statuses = {
            'closing_time': datetime.utcnow()
        }
        requests.update_request(int(id_), dict_of_statuses)
        msg = f'Заявка {id_} закрыта'
    else:
        msg = f'Некорректные данные для изменения'

    logger.info('Closure request has been processed')
    await message.reply(msg)


@dp.message_handler(commands=['set'])
async def set_time(message: types.Message):
    """
    Prepares arguments and runs script of setting potential time to a repair request
    :param message: message from telegram chat
    """
    request = message.get_args()
    split_request = reg_expr(request)

    if None not in split_request.values() and requests.check_existence_of_id(split_request['id']):
        dict_of_statuses = {
            'potential_time': split_request['time']
        }

        requests.update_request(split_request['id'], dict_of_statuses)
        msg = f'Заявка {split_request["id"]} обновлена'
    else:
        msg = f'Некорректные данные для изменения'

    logger.info('Update request has been processed')
    await message.reply(msg)


@dp.message_handler(commands=['check'])
async def check_open_requests(message: types.Message):
    """
    Sends active repair requests
    :param message: message from telegram chat
    """
    open_requests_list = requests.get_open_requests()
    open_requests_str = open_req_to_string(open_requests_list) or 'Нет активных заявок'
    await message.reply(open_requests_str)
