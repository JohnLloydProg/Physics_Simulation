import pymunk as pm
import pygame as pg
from objects.pymunk_object import PymunkObject
from constraints.constraint import PymunkConstraint


class PivotJoint(PymunkConstraint):
    def __init__(self, body_a:PymunkObject|pm.Body, anchor_a:tuple[float, float]):
        super().__init__(body_a, anchor_a)

    def place(self, space:pm.Space) -> None:
        body_a, body_b = super().place()
        self.constraint = pm.PivotJoint(body_a, body_b, self.anchor_a, self.anchor_b)
        if (isinstance(self.body_a, PymunkObject) and isinstance(self.body_b, PymunkObject)):
            self.constraint.collide_bodies = False
        return super().place(space)

    def json(self) -> dict:
        data = super().json()
        data['type'] = 'PivotJoint'
        return data
    
    @staticmethod
    def from_json(data:dict, space:pm.Space, objects:list) -> 'PivotJoint':
        body_a, body_b = super().from_json(data, space, objects)

        pivot_joint = PivotJoint(body_a=body_a, anchor_a=data['anchor_a'])
        pivot_joint.set_body_b(body_b, data['anchor_b'])
        return pivot_joint
