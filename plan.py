

from rule import SteppableRule, Pass, NullAction
from item import Item
from coroutine import step
from types import GeneratorType

class Plan(Item):

    rule = SteppableRule(Pass,NullAction)
    user = None
    name = 'plan'

    def __call__(self,user):
        self.user = user
        call = self.rule(self)
        if isinstance(call,GeneratorType):
            while step(call): yield

