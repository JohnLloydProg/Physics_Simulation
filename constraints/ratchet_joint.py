import pygame as pg
import pymunk as pm
from objects.pymunk_object import PymunkObject
from constraints.constraint import PymunkConstraint
import math


class RatchetJoint(PymunkConstraint):
    def __init__(self, body_a: PymunkObject|pm.Body, anchor_a: tuple[float, float], phase:float=0, ratchet:float=math.pi/2):
        super().__init__(body_a, anchor_a)
        self.phase = phase
        self.ratchet = ratchet

    def properties(self) -> dict:
        return {'phase':self.phase, 'ratchet':self.ratchet}
    
    def place(self, space: pm.Space) -> None:
        body_a, body_b = super().place()
        self.constraint = pm.RatchetJoint(
            body_a, 
            body_b, 
            self.phase, 
            self.ratchet
        )
        self.constraint.collide_bodies = False
        return super().place(space)

    def json(self) -> dict:
        data = super().json()
        data['phase'] = self.phase
        data['ratchet'] = self.ratchet
        data['type'] = 'RatchetJoint'
        return data

    @staticmethod
    def from_json(data: dict, space:pm.Space, objects:list) -> 'RatchetJoint':
        body_a, body_b = PymunkConstraint.from_json(data, space, objects)
        anchor_a = data['anchor_a']
        anchor_b = data['anchor_b']
        
        constraint = RatchetJoint(body_a, anchor_a, phase=data['phase'], ratchet=data['ratchet'])
        constraint.set_body_b(body_b, anchor_b)
        return constraint
