import pymunk as pm
import pygame as pg
from constraints.constraint import PymunkConstraint
from objects.pymunk_object import PymunkObject


class SimpleMotor(PymunkConstraint):
    def __init__(self, body_a: PymunkObject|pm.Body, anchor_a: tuple[float, float], rate:float=1):
        super().__init__(body_a, anchor_a)
        self.rate = rate

    def properties(self) -> dict:
        return {'rate':self.rate}
    
    def place(self, space: pm.Space) -> None:
        body_a, body_b = super().place()
        self.constraint = pm.SimpleMotor(
            body_a, 
            body_b, 
            self.rate
        )
        self.constraint.collide_bodies = False
        return super().place(space)

    def json(self) -> dict:
        data = super().json()
        data['rate'] = self.rate
        data['type'] = 'SimpleMotor'
        return data

    @staticmethod
    def from_json(data: dict, space:pm.Space, objects:list) -> 'SimpleMotor':
        body_a, body_b = PymunkConstraint.from_json(data, space, objects)
        anchor_a = data['anchor_a']
        anchor_b = data['anchor_b']
        
        motor = SimpleMotor(body_a, anchor_a, rate=data['rate'])
        motor.set_body_b(body_b, anchor_b)
        return motor
