

from rule import SteppableRule, Pass, NullAction
from item import Item
from coroutine import step
from types import GeneratorType

class Plan(Item):

    rule = SteppableRule(Pass,NullAction)
    user = None

    def __call__(self,user):
        self.user = user
        call = rule(self)
        if isinstance(call,GeneratorType):
            while step(call): yield

