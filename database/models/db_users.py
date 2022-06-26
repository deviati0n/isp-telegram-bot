import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

from project.project_context import ProjectContext

base = declarative_base()
context = ProjectContext()
engine = sa.create_engine(context.database_bill_config.db_connection)


class Users(base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.String(100), nullable=False)
    balance = sa.Column(sa.Float)
    date_contract = sa.Column(sa.Date)
    date_last_payment = sa.Column(sa.DateTime)
    group = sa.Column(sa.String)
    active = sa.Column(sa.Boolean)


if __name__ == '__main__':
    base.metadata.drop_all(engine)
    base.metadata.create_all(engine)
