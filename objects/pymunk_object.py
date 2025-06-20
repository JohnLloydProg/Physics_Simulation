import pymunk as pm
import pygame as pg
import math


class PymunkObject:
    surface:pg.Surface
    body:pm.Body|None = None
    shape:pm.Shape
    position:tuple[int, int]

    def __init__(self, id:int, mass:float=10.0, friction:float=0.5, elasticity:float=0.5, body_type:int=pm.Body.DYNAMIC):
        self.id = id
        self.mass = mass
        self.friction = friction
        self.elasticity = elasticity
        self.body_type = body_type
        self.z_index = 0
    
    def place(self, space:pm.Space) -> None:
        self.body = pm.Body(body_type=self.body_type)
        self.body.position = self.position
    
    def move_front(self):
        self.z_index += 1
    
    def move_back(self):
        self.z_index -= 1
    
    def clicked(self, event:pg.event.Event, consumed:list, space:pm.Space) -> tuple[float, float]:
        if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and event.type not in consumed):
            hit = space.point_query_nearest(pm.Vec2d(*event.pos), 0, pm.ShapeFilter())
            if (hit):
                if (hit.shape == self.shape):
                    position = self.body.position
                    consumed.append(event)
                    return (position[0] - event.pos[0], position[1] - event.pos[1])
        return None

    @staticmethod
    def from_json(data:dict) -> 'PymunkObject':
        return
    
    def json(self) -> dict:
        return {
            'id': self.id,
            'position':self.position,
            'mass':self.mass,
            'friction':self.friction,
            'elasticity':self.elasticity,
            'body_type':self.body_type
        }

    def set_position(self, new_pos:tuple[int, int]) -> None:
        self.position = new_pos
        self.body.position = new_pos 
    
    def reset(self) -> None:
        self.body.position = self.position
        self.body.angle = 0
        self.body.velocity = (0, 0)
        self.body.angular_velocity = 0
    
    def remove(self, space:pm.Space) -> None:
        if (self.body):
            space.remove(self.body, self.shape)
    
    def draw(self, window:pg.Surface) -> None:
        surface = pg.transform.rotate(self.surface, math.degrees(self.body.angle) * -1) if (self.body) else self.surface
        position = self.body.position if (self.body) else self.position
        window.blit(surface, surface.get_rect(center=position))
