from typing import List
from flask_restx import Model

from .issue import Issue


class Newspaper(object):
    def __init__(self, paper_id: int, name: str, frequency: int, price: float):
        self.paper_id: int = paper_id
        self.name: str = name
        self.frequency: int = frequency  # the issue frequency (in days)
        self.price: float = price  # the monthly price
        self.issues: List[Issue] = []
        self.subscribers = []

    def __eq__(self, other):
        return (self.name == other.name) and (self.frequency == other.frequency) and (self.price == other.price)
