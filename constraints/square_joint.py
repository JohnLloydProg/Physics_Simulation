import pygame as pg
import pymunk as pm
from constraints.constraint import PymunkConstraint


class SquareJoint(PymunkConstraint):
    def __init__(self, body_a, anchor_a):
        super().__init__(body_a, anchor_a)

    def place(self, space:pm.Space) -> None:
        body_a, body_b = super().place()
        pivot = pm.PivotJoint(body_a, body_b, self.anchor_a, self.anchor_b)
        pivot.collide_bodies = False
        gear = pm.GearJoint(body_a, body_b, 0, 1)
        self.constraint = (pivot, gear)
        space.add(pivot, gear)
    
    def remove(self, space:pm.Space) -> None:
        if (self.constraint):
            space.remove(*self.constraint)
        else:
            raise ValueError("Constraint not defined. Please define the constraint before removing it from the space.")
    
    def json(self) -> dict:
        data = super().json()
        data['type'] = 'SquareJoint'
        return data

    @staticmethod
    def from_json(data:dict, space:pm.Space, objects:list) -> 'SquareJoint':
        body_a, body_b = super().from_json(data, space, objects)

        square_joint = SquareJoint(body_a=body_a, anchor_a=data['anchor_a'])
        square_joint.set_body_b(body_b, data['anchor_b'])
        return square_joint

