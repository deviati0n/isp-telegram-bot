import asyncio
import datetime
import os
from datetime import datetime

from project.log_lib import get_logger
from project.project_context import ProjectContext

logger = get_logger('logs')


def reg_expr(full_request: str) -> dict[str, datetime | None | int]:
    """
    Splits a request string to request id and a date
    :param full_request: request from a telegram
    :return: dict with request id and date
    """
    time_, id_ = full_request.rsplit(' ', 1)

    try:
        time_ = datetime.strptime(time_, '%d.%m.%Y %H:%M')
        id_ = int(id_)
    except ValueError:
        time_, id_ = None, None

    return dict(time=time_, id=id_)


def open_req_to_string(request_list: list) -> str:
    """
    Creates a string of active repair requests
    :param request_list: list of repair requests
    :return: string of active repair requests
    """
    response_list = []
    for el in request_list:
        if el.potential_time is not None:
            response_list.append(f'• id: {str(el.id)} — {el.request}\n{el.potential_time}')
        else:
            response_list.append(f'• id: {str(el.id)} — {el.request}')

    return '\n'.join(response_list)


async def clear_logs():
    """
    Clears old log files
    """
    context = ProjectContext()

    while True:
        for folder in (context.logs_path,):
            for i in (os.listdir(folder)):

                creation_time_unix = os.path.getmtime(os.path.join(folder, i))
                creation_time = datetime.datetime.fromtimestamp(creation_time_unix)

                if creation_time < datetime.datetime.now() - datetime.timedelta(days=2):
                    os.remove(os.path.join(folder, i))
                    logger.info(f'{i} has been removed')

        await asyncio.sleep(context.logger_time)
