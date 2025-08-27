import pymunk as pm
import pygame as pg
from objects.pymunk_object import PymunkObject
from constraints.constraint import PymunkConstraint


class GearJoint(PymunkConstraint):
    def __init__(self, body_a:PymunkObject|pm.Body, anchor_a:tuple[float, float], phase:float=0.3, ratio:float=0.3):
        super().__init__(body_a, anchor_a)
        self.phase = phase
        self.ratio = ratio

    def properties(self) -> dict:
        return {'phase':self.phase, 'ratio':self.ratio}

    def place(self, space:pm.Space) -> None:
        body_a, body_b = super().place()
        self.constraint = pm.GearJoint(a=body_a, b=body_b, phase=self.phase, ratio=self.ratio)
        return super().place(space)

    def json(self) -> dict:
        data = super().json()
        data['phase'] = self.phase
        data['ratio'] = self.ratio
        data['type'] = 'GearJoint'
        return data
    
    @staticmethod
    def from_json(data:dict, space:pm.Space, objects:list) -> 'GearJoint':
        body_a, body_b = super().from_json(data, space, objects)

        gear_joint = GearJoint(body_a=body_a, phase=data['phase'], ratio=data['ratio'])
        gear_joint.set_body_b(body_b)
        return gear_joint

