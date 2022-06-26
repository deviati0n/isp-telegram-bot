import asyncio
import datetime
import os

from project.log_lib import get_logger
from project.project_context import ProjectContext

logger = get_logger('logs')


def list_str_to_int(initial_list: list):
    final_list = []

    for el in initial_list:
        if str.isdigit(el):
            final_list.append(int(el))
        else:
            return None

    return final_list


def reg_expr(full_request: str):
    time_, id_ = full_request.rsplit(' ', 1)

    try:
        time_ = datetime.datetime.strptime(time_, '%d.%m.%Y %H:%M')
        id_ = int(id_)
    except ValueError:
        time_, id_ = None, None

    return dict(time=time_, id=id_)


def open_req_to_string(request_list: list) -> str:
    response_string = [f'id: {str(el.id)} — {el.request}' for el in request_list]
    return '\n'.join(response_string)


async def clear_logs():
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
