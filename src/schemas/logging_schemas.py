from enum import Enum

from pydantic import BaseModel


class Level(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


ANSI = {
    Level.INFO: {"before": "\u001b[1;47;32m", "after": "\u001b[0;0m", "mention": ""},
    Level.WARNING: {"before": "\u001b[0;47;33m", "after": "\u001b[0;0m", "mention": ""},
    Level.ERROR: {"before": "\u001b[0;47;31m", "after": "\u001b[0;0m", "mention": "@here \n"},
    Level.CRITICAL: {"before": "\u001b[0;41;37m", "after": "\u001b[0;0m", "mention": "@everyone \n"},
}


class LoggingMessage(BaseModel):
    level: Level
    message: str

    def __str__(self):
        return f"""{self.level.value} - {self.message}"""

    def __repr__(self):
        return str(self)

    def get_ansi(self):
        return f"""{ANSI[self.level]["mention"]}```ansi\n{ANSI[self.level]["before"]} {self.level.value} {ANSI[self.level]["after"]} {self.message}\n```"""


class SendLogInput(BaseModel):
    logging_message: LoggingMessage
    channel_id: int
