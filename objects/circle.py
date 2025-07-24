import pygame as pg
from pygame.event import Event
import pymunk as pm
from objects.pymunk_object import PymunkObject
from ui import ButtonBehavior
import math


class Circle(PymunkObject):
    def __init__(self, id:int, position:tuple[int, int], radius:float, mass:float=10.0, friction:float=0.5, elasticity:float=0.5, body_type:int=pm.Body.DYNAMIC, group_id:int=0):
        super().__init__(id, mass, friction, elasticity, body_type, group_id)
        self.position = position
        self.radius = radius

        self.surface = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
        
        self.mask = pg.mask.from_surface(self.surface)
    
    @staticmethod
    def from_json(data:dict) -> 'Circle':
        circle = Circle(
            id = data['id'],
            position=data['position'],
            radius=data['radius'],
            mass=data['mass'],
            friction=data['friction'],
            elasticity=data['elasticity'],
            body_type=data['body_type'],
            group_id=data['group_id']
        )
        circle.z_index = data['z_index']
        return circle
    
    def json(self) -> dict:
        data = super().json()
        data['radius'] = self.radius
        data['type'] = 'Circle'
        return data
    
    def place(self, space:pm.Space) -> None:
        super().place(space)

        self.shape = pm.Circle(self.body, self.radius)
        self.shape.group_id = self.group_id
        self.shape.collision_type = 1
        self.shape.mass = self.mass
        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity

        if (self.body):
            space.add(self.body, self.shape)
    
    def draw(self, window:pg.Surface) -> None:
        self.surface.fill((255, 255, 255, 0))
        color = (255, 0, 0) if (self.body.body_type == pm.Body.DYNAMIC) else (255, 100, 100)
        pg.draw.circle(self.surface, color, (self.radius, self.radius), self.radius)
        pg.draw.line(self.surface, (0, 0, 0), (self.radius, self.radius), (self.radius*2, self.radius), 3)
        super().draw(window)
        
