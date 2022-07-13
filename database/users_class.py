import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from database.models.db_users import Users
from project.project_context import ProjectContext


class UsersFunction:
    """
    A class for interacting with Users Table
    """
    context = ProjectContext()
    engine = sa.create_engine(context.database_bill_config.db_connection)

    def __init__(self):
        self.Session = sessionmaker(self.engine)
        self.session = self.Session()

    def commit(self) -> None:
        """
        Commits the current changes
        """
        self.session.commit()

    def clear_table(self) -> None:
        """
        Clears a Users table
        """
        self.session.query(
            Users
        ).delete(
            synchronize_session='fetch'
        )
        self.commit()

    def add_user(self, users: list['Users']) -> None:
        """
        Adds users to the Users table
        :param users: list of users
        """
        self.clear_table()
        self.session.bulk_save_objects(users)
        self.commit()

    def find_users(self, user_login: str) -> bool:
        """
        User search by login
        :param user_login: user login
        :return: bool value of user existence  in table
        """
        request = self.session.query(
            Users
        ).filter(
            Users.login == user_login
        ).first()

        if request:
            return True

    def clear_all_active(self) -> None:
        """
        Updates the activity status for all users. Sets statuses to False
        """
        self.session.query(
            Users
        ).update(
            {Users.active: False}
        )

        self.commit()

    def update_active_status(self, user_login: str) -> None:
        """
        Updates the activity status for user. Sets status to True
        :param user_login: user login
        """
        self.session.query(
            Users
        ).filter(
            Users.login == user_login
        ).update(
            {Users.active: True}
        )

        self.commit()


if __name__ == "__main__":
    ...
