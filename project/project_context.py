import contextlib
import os
from os import path

import yaml

from utils import data_classes as dc


class ProjectContext:

    def __init__(self):
        self.project_path = path.dirname(path.realpath(__file__))
        config_path = path.join(self.project_path, '../utils/config.yaml')
        self.logs_path = path.join(self.project_path, 'logs')
        self.driver_path = r'E:\Chromedriver.exe'

        for folder in (self.logs_path,):
            if not path.exists(folder):
                with contextlib.suppress(Exception):
                    os.mkdir(folder)

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        billing = self.config['billing']
        self.billing_config = dc.BillingConfig(**billing)

        bot = self.config['bot']
        self.bot_config = dc.BotConfig(**bot)

        database_bill = self.config['database_bill']
        self.database_bill_config = dc.DatabaseConfig(**database_bill)

        database_req = self.config['database_req']
        self.database_req_config = dc.DatabaseConfig(**database_req)

        self.logger_time = self.config['logger']['loop_time']

    @property
    def path(self) -> str:
        return self.driver_path
