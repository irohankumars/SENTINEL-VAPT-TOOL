from abc import ABC, abstractmethod

class ScannerError(RuntimeError):
    pass

class BaseScanner(ABC):
    @abstractmethod
    def run(self, target: str) -> list[dict]:
        raise NotImplementedError
