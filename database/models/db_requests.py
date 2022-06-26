from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

from project.project_context import ProjectContext

context = ProjectContext()
engine = sa.create_engine(context.database_req_config.db_connection)
base = declarative_base()


class Requests(base):
    __tablename__ = 'request_data'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    request = sa.Column(sa.String(100), nullable=False)
    creation_time = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    potential_time = sa.Column(sa.DateTime)
    closing_time = sa.Column(sa.DateTime)


if __name__ == '__main__':
    base.metadata.drop_all(engine)
    base.metadata.create_all(engine)
