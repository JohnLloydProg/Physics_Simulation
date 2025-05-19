import pymunk as pm
import pygame as pg
from objects.pymunk_object import PymunkObject
import math


class Rectangle(PymunkObject):
    def __init__(self, corner_1, corner_2, mass = 10, friction = 0.5, elasticity = 0.5, body_type = pm.Body.DYNAMIC):
        super().__init__(mass, friction, elasticity, body_type)
        self.corner_1 = corner_1
        self.corner_2 = corner_2
        self.position = ((corner_1[0] + corner_2[0])/2,(corner_1[1] + corner_2[1])/2)
        width = abs(corner_1[0] - corner_2[0])
        height = abs(corner_1[1] - corner_2[1])

        self.points = [(-width/2, -height/2), (width/2, -height/2), (width/2, height/2), (-width/2, height/2)]
        self.surface:pg.Surface = pg.Surface((width, height), pg.SRCALPHA)
        self.surface.fill((0, 255, 0))
    
    @classmethod
    def from_json(self, data:dict) -> 'Rectangle':
        return Rectangle(
            corner_1=data['corner_1'],
            corner_2=data['corner_2'],
            mass=data['mass'],
            friction=data['friction'],
            elasticity=data['elasticity'],
            body_type=data['body_type']
        )
    
    def json(self) -> dict:
        data = super().json()
        data['corner_1'] = self.corner_1
        data['corner_2'] = self.corner_2
        data['type'] = 'Rectangle'
        return data
    
    def place(self, space:pm.Space) -> None:
        super().place(space)

        self.shape = pm.shapes.Poly(self.body, self.points)
        self.shape.mass = self.mass
        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity

        if (self.body):
            space.add(self.body, self.shape)

        
        



