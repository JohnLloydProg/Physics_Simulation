import pygame as pg
import pymunk as pm
from objects.pymunk_object import PymunkObject
from constraints.constraint import PymunkConstraint
import math

class StringConstraint(PymunkConstraint):

    def __init__(self, body_a:PymunkObject|pm.Body, anchor_a:tuple[int, int], max:float=None):
        super().__init__(body_a, anchor_a)
        self.max = max
    
    def properties(self):
        return {"max": self.max}
    
    def place(self, space: pm.Space) -> None:
        body_a, body_b = super().place()
        p1 = body_a.local_to_world(self.anchor_a)
        p2 = body_b.local_to_world(self.anchor_b)
        max = self.max if self.max else math.dist(p1, p2)
        self.constraint = pm.SlideJoint(
            body_a, 
            body_b, 
            self.anchor_a, 
            self.anchor_b, 
            0, 
            max
        )
        return super().place(space)

    def json(self) -> dict:
        data = super().json()
        data['type'] = 'StringConstraint'
        data['length'] = self.max
        return data
    
    @staticmethod
    def from_json(data:dict, space:pm.Space, objects:list) -> 'StringConstraint':
        body_a, body_b = PymunkConstraint.from_json(data, space, objects)
        anchor_a = data['anchor_a']
        anchor_b = data['anchor_b']
        
        string = StringConstraint(body_a, anchor_a)
        string.max = data['length']
        string.set_body_b(body_b, anchor_b)
        return string
