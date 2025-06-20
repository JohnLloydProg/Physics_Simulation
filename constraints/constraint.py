import pygame as pg
import pymunk as pm 
from objects.pymunk_object import PymunkObject


class PymunkConstraint:
    constraint:pm.Constraint
    body_b: pm.Body = None

    def __init__(self, body_a: PymunkObject|pm.Body, anchor_a: tuple[float, float]):
        self.body_a = body_a
        self.anchor_a = anchor_a
        self.constraint = None
    
    def set_body_b(self, body_b: PymunkObject|pm.Body, anchor_b: tuple[float, float]) -> None:
        self.body_b = body_b
        self.anchor_b = anchor_b
    
    def json(self) -> dict:
        data = {
            'body_a': self.body_a.id if (isinstance(self.body_a, PymunkObject)) else 'space',
            'anchor_a': self.anchor_a,
            'body_b': self.body_b.id if (isinstance(self.body_b, PymunkObject)) else 'space',
            'anchor_b': self.anchor_b if hasattr(self, 'anchor_b') else None
        }
        return data
    
    def place(self, space: pm.Space) -> None:
        if self.constraint:
            space.add(self.constraint)
        else:
            raise ValueError("Constraint not defined. Please define the constraint before placing it in the space.")
    
    def remove(self, space: pm.Space) -> None:
        if self.constraint:
            space.remove(self.constraint)
        else:
            raise ValueError("Constraint not defined. Please define the constraint before removing it from the space.")
    


