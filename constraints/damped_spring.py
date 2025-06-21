import pygame as pg
import pymunk as pm
from objects.pymunk_object import PymunkObject
from constraints.constraint import PymunkConstraint
import math


class DampedSpring(PymunkConstraint):
    def __init__(self, body_a: PymunkObject|pm.Body, anchor_a: tuple[float, float], stiffness:float=20, damping:float=0.3):
        super().__init__(body_a, anchor_a)
        self.stiffness = stiffness
        self.damping = damping

    def properties(self) -> dict:
        return {'stiffness':self.stiffness, 'damping':self.damping}
    
    def place(self, space: pm.Space) -> None:
        pos1_x = self.body_a.position[0] + self.anchor_a[0]
        pos1_y = self.body_a.position[1] + self.anchor_a[1]
        pos2_x = self.body_b.position[0] + self.anchor_b[0]
        pos2_y = self.body_b.position[1] + self.anchor_b[1]
        rest_length = math.dist((pos1_x, pos1_y), (pos2_x, pos2_y))
        body_a = self.body_a.body if (isinstance(self.body_a, PymunkObject)) else self.body_a
        body_b = self.body_b.body if (isinstance(self.body_b, PymunkObject)) else self.body_b
        self.constraint = pm.DampedSpring(
            body_a, 
            body_b, 
            self.anchor_a, 
            self.anchor_b, 
            rest_length=rest_length, 
            stiffness=self.stiffness, 
            damping=self.damping
        )
        return super().place(space)

    def json(self) -> dict:
        data = super().json()
        data['stiffness'] = self.stiffness
        data['damping'] = self.damping
        data['type'] = 'DampedSpring'
        return data

    @staticmethod
    def from_json(data: dict, space:pm.Space, objects:list) -> 'DampedSpring':
        body_a, body_b = PymunkConstraint.from_json(data, space, objects)
        anchor_a = tuple(data['anchor_a'])
        anchor_b = tuple(data['anchor_b'])
        
        spring = DampedSpring(body_a, anchor_a, stiffness=data['stiffness'], damping=data['damping'])
        spring.set_body_b(body_b, anchor_b)
        return spring



