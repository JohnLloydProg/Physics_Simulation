import pygame as pg
import pymunk as pm
from objects.pymunk_object import PymunkObject
from constraints.constraint import PymunkConstraint
import math


class DampedSpring(PymunkConstraint):
    def __init__(self, body_a: PymunkObject, anchor_a: tuple[float, float]):
        super().__init__(body_a)
        self.anchor_a = anchor_a
    
    def place(self, space: pm.Space) -> None:
        pos1_x = self.body_a.body.position[0] + self.anchor_a[0]
        pos1_y = self.body_a.body.position[1] + self.anchor_a[1]
        pos2_x = self.body_b.body.position[0] + self.anchor_b[0]
        pos2_y = self.body_b.body.position[1] + self.anchor_b[1]
        rest_length = math.dist((pos1_x, pos1_y), (pos2_x, pos2_y))
        self.constraint = pm.DampedSpring(
            self.body_a.body, 
            self.body_b.body, 
            self.anchor_a, 
            self.anchor_b, 
            rest_length=rest_length, 
            stiffness=20, 
            damping=0.3
        )
        return super().place(space)

    def json(self) -> dict:
        data = super().json()
        data['type'] = 'DampedSpring'
        return data

    def from_json(self, data: dict) -> 'DampedSpring':
        body_a = PymunkObject.from_json(data['body_a'])
        body_b = PymunkObject.from_json(data['body_b'])
        anchor_a = tuple(data['anchor_a'])
        anchor_b = tuple(data['anchor_b'])
        
        spring = DampedSpring(body_a, anchor_a)
        spring.set_body_b(body_b, anchor_b)
        return spring



