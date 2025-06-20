import pygame as pg
import pymunk as pm
from objects.pymunk_object import PymunkObject
from constraints.constraint import PymunkConstraint


class PinJoint(PymunkConstraint):
    def __init__(self, body_a:PymunkObject, anchor_a:tuple[float, float]):
        super().__init__(body_a, anchor_a)
    
    def place(self, space:pm.Space) -> None:
        body_a = self.body_a.body if (isinstance(self.body_a, PymunkObject)) else self.body_a
        body_b = self.body_b.body if (isinstance(self.body_b, PymunkObject)) else self.body_b
        self.constraint = pm.PinJoint(body_a, body_b, self.anchor_a, self.anchor_b)
        return super().place(space)

    def json(self) -> dict:
        data = super().json()
        data['type'] = 'PinJoint'
        return data
    
    @staticmethod
    def from_json(data:dict, space:pm.Space, objects:list) -> 'PinJoint':
        body_a, body_b = PymunkConstraint.from_json(data, space, objects)
        anchor_a = tuple(data['anchor_a'])
        anchor_b = tuple(data['anchor_b'])
        
        pinJoint = PinJoint(body_a, anchor_a)
        pinJoint.set_body_b(body_b, anchor_b)
        return pinJoint

