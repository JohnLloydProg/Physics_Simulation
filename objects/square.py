import pygame as pg
import pymunk as pm
from objects.rectangle import Rectangle
import math


class Square(Rectangle):
    def __init__(self, id, corner_1, corner_2, angle=0, mass = 10, friction = 0.5, elasticity = 0.5, body_type = pm.Body.DYNAMIC, group_id:int=0):
        super().__init__(id, corner_1, corner_2, angle, mass, friction, elasticity, body_type, group_id)
        side = (math.dist(corner_1, corner_2) * math.sqrt(2))/2

        self.points = [(-side/2, -side/2), (side/2, -side/2), (side/2, side/2), (-side/2, side/2)]
        self.surface = pg.Surface((side, side), pg.SRCALPHA)
    
    @staticmethod
    def from_json(data:dict) -> 'Square':
        square = Square(
            id = data['id'],
            corner_1=data['corner_1'],
            corner_2=data['corner_2'],
            angle=data['angle'],
            mass=data['mass'],
            friction=data['friction'],
            elasticity=data['elasticity'],
            body_type=data['body_type'],
            group_id=data['group_id']
        )
        square.z_index = data['z_index']
        return square
    
    def json(self) -> dict:
        data = super().json()
        data['type'] = 'Square'
        return data
    
    def draw(self, window:pg.Surface, selected:bool) -> None:
        color = (0, 0, 255) if (self.body.body_type == pm.Body.DYNAMIC) else (100, 100, 255)
        self.surface.fill(color)
        pg.draw.rect(self.surface, (0, 0, 0), (0, 0, self.surface.get_width(), self.surface.get_height()), 3 if not selected else 6)
        super().draw(window)




