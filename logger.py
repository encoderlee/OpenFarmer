import logging
import sys
from logging import handlers
import os
from settings import cfg

_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)
log = logging.LoggerAdapter(_log, {"tag": "global"})


def init_loger(loger_name: str):
    handler = logging.StreamHandler(sys.stdout)
    #logging_format = logging.Formatter("[%(asctime)s][%(levelname)s][%(process)d][%(tag)s]: %(message)s")
    logging_format = logging.Formatter("[%(asctime)s][%(tag)s]: %(message)s","%Y-%m-%d %H:%M:%S")
    handler.setFormatter(logging_format)
    logging.getLogger().addHandler(handler)
    if not os.path.exists(cfg.path_logs):
        os.makedirs(cfg.path_logs)
    log_file_name = "{0}.log".format(loger_name)
    log_file_path = os.path.join(cfg.path_logs, log_file_name)
    handler = logging.handlers.TimedRotatingFileHandler(log_file_path, when="midnight", encoding='UTF-8',
                                                        backupCount=30)
    handler.suffix = "%Y-%m-%d"
    handler.setFormatter(logging_format)
    logging.getLogger().addHandler(handler)

