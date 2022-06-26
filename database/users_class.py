import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from database.models.db_users import Users
from project.project_context import ProjectContext


class UsersFunction:
    context = ProjectContext()
    engine = sa.create_engine(context.database_bill_config.db_connection)

    def __init__(self):
        self.Session = sessionmaker(self.engine)
        self.session = self.Session()

    def commit(self):
        self.session.commit()

    def clear_table(self):
        self.session.query(
            Users
        ).delete(
            synchronize_session='fetch'
        )
        self.commit()

    def add_user_q(self, users: list['Users']) -> None:
        self.clear_table()
        self.session.bulk_save_objects(users)
        self.commit()

    def find_users_q(self, user_login: str) -> bool:
        request = self.session.query(
            Users
        ).filter(
            Users.login == user_login
        ).first()

        if request:
            return True

    def clear_all_active(self) -> None:
        self.session.query(
            Users
        ).update(
            {Users.active: False}
        )

        self.commit()

    def update_active_status_q(self, user_login: str) -> None:
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
