from abc import ABCMeta, abstractmethod


class MarkdownService(metaclass=ABCMeta):
    @abstractmethod
    def to_html(self, text: str) -> str:
        raise NotImplementedError
