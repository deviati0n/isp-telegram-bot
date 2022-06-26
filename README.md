# ISP Telegram Bot

The bot was written to automate part of the work of technical support workers. 
It allows you to keep records of daily or monthly cash transfers.
The bot also allows you to control requests for repair work (create, determine
the time of execution, close and view active ones).

## Requirements
``` 
SQLAlchemy~=1.4.37
aiogram~=2.20
parsel~=1.6.0
selenium~=4.2.0
psycopg2~=2.9.3
coloredlogs~=15.0.1
concurrent_log_handler~=0.9.20
```

## Install 
```shell
$ git clone https://github.com/deviati0n/isp-telegram-bot.git <project_name>
$ cd <project_name>
$ pip install -r requirements.txt
```

## Run project

Rename `default.yaml` to `config.yaml` and change the values to your own. 

### Run bot
  
```shell
$ python telegram_bot.py
```





