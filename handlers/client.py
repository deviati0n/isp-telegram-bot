from calendar import monthrange
from datetime import date, datetime, timedelta

from aiogram import types
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, bold

from bot_function.billing_class import BillingFunction
from create_bot import bot
from create_bot import dp
from database.requests_class import RequestsFunction
from project.log_lib import get_logger
from utils.utils_functions import reg_expr, open_req_to_string

billing = BillingFunction()
requests = RequestsFunction()
logger = get_logger('logs')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот-помощник для интернет-провайдера.")


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    msg = text(bold('Я могу ответить на следующие команды:'),
               '/report', '/reportmonth', '/add', '/close', '/set', '/check', sep='\n')
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['report'])
async def report_billing(message: types.Message):
    received_message = message.get_args().split(' ')
    default_date = [date.today() - timedelta(days=1)]

    try:
        received_date = [datetime.strptime(d, '%Y-%m-%d').date() for d in received_message]
    except ValueError:
        received_date = received_message

    date_bill = received_date if any(received_message) else default_date

    date_bill = {'first_date': date_bill[0], 'last_date': date_bill[0]} if len(date_bill) == 1 \
        else {'first_date': date_bill[0], 'last_date': date_bill[1]}

    report = billing.billing_report(date_bill)
    await bot.send_message(message.from_user.id, report, reply_to_message_id=message.message_id)


@dp.message_handler(commands=['reportmonth'])
async def accountants_report(message: types.Message):
    prev_month = date.today().month - 1
    max_day = monthrange(date.today().year, prev_month)[1]
    date_bill = {'first_date': date.fromisoformat(f'2022-0{prev_month}-01'),
                 'last_date': date.fromisoformat(f'2022-0{prev_month}-{max_day}')}
    report_month = billing.report_acc_bill(date_bill)
    await bot.send_message(message.from_user.id, report_month, reply_to_message_id=message.message_id)


@dp.message_handler(commands=['activeUser'])
async def active_user(message: types.Message):
    billing.receive_user_data()
    await message.answer('Таблица с пользователя была обновлена')


@dp.message_handler(commands=['add'])
async def add_request(message: types.Message):
    request = message.get_args()
    requests.add_request(request)

    logger.info('Adding request has been processed')
    await bot.send_message(message.from_user.id, f'Заявка "{request}" добавлена', reply_to_message_id=message.message_id)


@dp.message_handler(commands=['close'])
async def close_request(message: types.Message):
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
    await bot.send_message(message.from_user.id, msg, reply_to_message_id=message.message_id)


@dp.message_handler(commands=['set'])
async def set_time(message: types.Message):
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
    await bot.send_message(message.from_user.id, msg, reply_to_message_id=message.message_id)


@dp.message_handler(commands=['check'])
async def check_open_requests(message: types.Message):
    open_requests_list = requests.check_open_requests()
    open_requests_str = open_req_to_string(open_requests_list)
    await bot.send_message(message.from_user.id, open_requests_str, reply_to_message_id=message.message_id)
