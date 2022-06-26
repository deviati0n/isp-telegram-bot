from dataclasses import dataclass
from typing import Dict


@dataclass
class BillingConfig:
    url: str
    login: str
    password: str
    plan: int


@dataclass
class BotConfig:
    token: str


@dataclass
class MirandaConfig:
    login: str
    password: str


@dataclass
class BillingReport:
    billing_data: Dict[str, float]

    def report(self) -> str:
        repReq = f'Заявки - {self.billing_data["dayReq"]}/{self.billing_data["periodReq"]}'
        repCon = f'Подключения - {self.billing_data["dayCon"]}/{self.billing_data["periodCon"]}'
        repSum = f'Сумма - {self.billing_data["daySum"]}/{self.billing_data["periodSum"]}/' \
                 f'{self.billing_data["percent"]}%'

        return f'{repReq}\n{repCon}\n{repSum}'


@dataclass
class DatabaseConfig:
    user: str
    password: str
    host: str
    port: int
    name: str

    @property
    def db_connection(self) -> str:
        return f'postgresql://{self.user}:{self.password}@' \
               f'{self.host}:{self.port}/{self.name}'



