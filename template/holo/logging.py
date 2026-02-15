import logging

from pythonjsonlogger import json

from holo.config import config


class HoloJsonEncoder(json.JsonEncoder):
    """
    Custom encoder to ensure datetime is formatted to our standards.
    """

    def format_datetime_obj(self, o) -> str:
        return o.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class HoloJsonFormatter(json.JsonFormatter):
    """
    Custom formatter to join the default logger fields into a new one.
    """

    def add_fields(self, log_record, record, message_dict) -> None:
        super().add_fields(log_record, record, message_dict)

        log_record["sender"] = f"{record.name}:{record.funcName}::{record.lineno}"


class UvicornAccessFilter(logging.Filter):
    def __init__(self, endpoints: list[str]) -> None:
        self._endpoints = endpoints

    def filter(self, record: logging.LogRecord) -> bool:
        if config.service.TESTING:
            return False

        # Example args: ('172.21.0.1:64898', 'GET', '/openapi.json', '1.1', 200)
        try:
            path: str
            if isinstance(record.args, dict) and "U" in record.args:
                path = record.args["U"]
            else:
                path = record.args[2]
        except IndexError:
            return True
        else:
            return not any(path.startswith(f"{endpoint}") for endpoint in self._endpoints)
