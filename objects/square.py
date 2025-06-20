import pygame as pg
import pymunk as pm
from objects.rectangle import Rectangle
import math


class Square(Rectangle):
    def __init__(self, id, corner_1, corner_2, mass = 10, friction = 0.5, elasticity = 0.5, body_type = pm.Body.DYNAMIC):
        super().__init__(id, corner_1, corner_2, mass, friction, elasticity, body_type)
        side = (math.dist(corner_1, corner_2) * math.sqrt(2))/2

        self.points = [(-side/2, -side/2), (side/2, -side/2), (side/2, side/2), (-side/2, side/2)]
        self.surface = pg.Surface((side, side), pg.SRCALPHA)
        self.surface.fill((0, 0, 255))
    
    @staticmethod
    def from_json(data:dict) -> 'Square':
        return Square(
            id = data['id'],
            corner_1=data['corner_1'],
            corner_2=data['corner_2'],
            mass=data['mass'],
            friction=data['friction'],
            elasticity=data['elasticity'],
            body_type=data['body_type']
        )
    
    def json(self) -> dict:
        data = super().json()
        data['type'] = 'Square'
        return data




