from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models.db_requests import Requests
from project.project_context import ProjectContext


class RequestsFunction:
    """
    A class for interacting with Requests Table
    """
    context = ProjectContext()
    engine = create_engine(context.database_req_config.db_connection)

    def __init__(self):
        self.Session = sessionmaker(self.engine)
        self.session = self.Session()

    def commit(self):
        """
        Commits the current changes
        """
        self.session.commit()

    def add_request(self, request: str) -> None:
        """
        Adds a new request to the database
        :param: request: new request
        :return: None
        """

        new_request = Requests(
            request=request
        )
        self.session.add(new_request)

        self.commit()

    def check_existence_of_id(self, id_: int) -> Optional[bool]:
        """
        Checks existence of id in Requests table and that the request was not closed earlier
        :param id_: id of request
        :return: bool value of existence or None
        """
        request = self.session.query(
            Requests
        ).filter(
            Requests.id == id_
        ).first()

        if request and not request.closing_time:
            return True

    def get_open_requests(self) -> list:
        """
        Gets a list of open requests from Requests table
        :return: list of open requests
        """

        open_requests_q = self.session.query(
            Requests.id,
            Requests.request,
            Requests.potential_time
        ).filter(
            Requests.closing_time.is_(None)
        ).all()

        return open_requests_q

    def update_request(self, id_: int, dict_of_statuses: dict) -> Optional[bool]:
        """
        Updates closing time or potential time of request from Requests table
        :param id_: id of request
        :param dict_of_statuses: dict with values of closing time and potential time
        :return: bool value of updating or None
        """
        dict_of_time_keys = {
            'closing_time': Requests.closing_time.key,
            'potential_time': Requests.potential_time.key
        }

        request = self.session.query(
            Requests
        ).filter(
            Requests.id == id_
        )

        for k, v in dict_of_statuses.items():
            if v:
                request = request.update({
                    dict_of_time_keys[k]: v
                })

        self.commit()

        if request:
            return True


if __name__ == "__main__":
    ...
