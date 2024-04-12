from .issue import Issue
from .newspaper import Newspaper

from typing import List


class Subscriber:
    def __init__(self, ID: int, name: str, address: str):
        self.ID: int = ID
        self.name: str = name
        self.address: str = address
        self.newspaper_list: List[Newspaper] = []  # subscription list
        self.issues_list: List[Issue] = []  # all received issues (including issues without subscription)

    def __eq__(self, other):
        return (self.name == other.name) and (self.address == other.address)
