import abc
from logging import Logger
from naga import Naga

class AbstractPrinter(metaclass=abc.ABCMeta):

    def __init__(self, naga: "Naga", logger: Logger) -> None:
        self.naga = naga
        self.logger = logger

    def info(self, info: str) -> None:
        if self.logger:
            self.logger.info(info)

    @abc.abstractmethod
    def output(self, filename: str):
        pass



