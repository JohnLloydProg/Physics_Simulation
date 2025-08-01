import pymunk as pm
import pygame as pg
from objects.pymunk_object import PymunkObject
import math


class Rectangle(PymunkObject):
    def __init__(self, id, corner_1, corner_2, mass = 10, friction = 0.5, elasticity = 0.5, body_type = pm.Body.DYNAMIC, group_id:int=0):
        super().__init__(id, mass, friction, elasticity, body_type, group_id)
        self.corner_1 = corner_1
        self.corner_2 = corner_2
        self.position = ((corner_1[0] + corner_2[0])/2,(corner_1[1] + corner_2[1])/2)
        width = abs(corner_1[0] - corner_2[0])
        height = abs(corner_1[1] - corner_2[1])

        self.points = [(-width/2, -height/2), (width/2, -height/2), (width/2, height/2), (-width/2, height/2)]
        self.surface:pg.Surface = pg.Surface((width, height), pg.SRCALPHA)
    
    @staticmethod
    def from_json(data:dict) -> 'Rectangle':
        rectangle = Rectangle(
            id = data['id'],
            corner_1=data['corner_1'],
            corner_2=data['corner_2'],
            mass=data['mass'],
            friction=data['friction'],
            elasticity=data['elasticity'],
            body_type=data['body_type'],
            group_id=data['group_id']
        )
        rectangle.z_index = data['z_index']
        return rectangle
    
    def json(self) -> dict:
        data = super().json()
        data['corner_1'] = self.corner_1
        data['corner_2'] = self.corner_2
        data['type'] = 'Rectangle'
        return data

    def set_position(self, new_pos:tuple[int, int]) -> None:
        x_dif = new_pos[0] - self.position[0]
        y_dif = new_pos[1] - self.position[1] 
        super().set_position(new_pos)
        self.corner_1 = (self.corner_1[0]+x_dif, self.corner_1[1]+y_dif)
        self.corner_2 = (self.corner_2[0]+x_dif, self.corner_2[1]+y_dif)
    
    def place(self, space:pm.Space) -> None:
        super().place(space)

        self.shape = pm.shapes.Poly(self.body, self.points)
        self.shape.group_id = self.group_id
        self.shape.collision_type = 1
        self.shape.mass = self.mass
        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity

        if (self.body):
            space.add(self.body, self.shape)
    
    def draw(self, window:pg.Surface) -> None:
        color = (0, 255, 0) if (self.body.body_type == pm.Body.DYNAMIC) else (100, 255, 100)
        self.surface.fill(color)
        super().draw(window)

        
        



