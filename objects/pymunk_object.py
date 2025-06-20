import pymunk as pk
import pygame as pg
import math


class PymunkObject:
    surface:pg.Surface
    body:pk.Body|None = None
    shape:pk.Shape
    position:tuple[int, int]

    def __init__(self, id:int, mass:float=10.0, friction:float=0.5, elasticity:float=0.5, body_type:int=pk.Body.DYNAMIC):
        self.id = id
        self.mass = mass
        self.friction = friction
        self.elasticity = elasticity
        self.body_type = body_type
        self.z_index = 0
    
    def place(self, space:pk.Space) -> None:
        self.body = pk.Body(body_type=self.body_type)
        self.body.position = self.position
    
    def move_front(self):
        self.z_index += 1
    
    def move_back(self):
        self.z_index -= 1
    
    def clicked(self, event:pg.event.Event, consumed:list) -> tuple[float, float]:
        if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and event.type not in consumed):
            surface = pg.transform.rotate(self.surface, math.degrees(self.body.angle) * -1) if (self.body) else self.surface
            position = self.body.position if (self.body) else self.position
            rect = surface.get_rect(center=position)
            if (rect.collidepoint(event.pos)):
                cursor_mask = pg.Mask((3, 3), True)
                mask = pg.mask.from_surface(surface)
                if (mask.overlap(cursor_mask, (event.pos[0] - rect.x, event.pos[1] - rect.y))):
                    offset = (position[0] - event.pos[0], position[1] - event.pos[1])
                    consumed.append(event)
                    return offset
        return None
    
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
    
    def remove(self, space:pk.Space) -> None:
        if (self.body):
            space.remove(self.body, self.shape)
    
    def draw(self, window:pg.Surface) -> None:
        surface = pg.transform.rotate(self.surface, math.degrees(self.body.angle) * -1) if (self.body) else self.surface
        position = self.body.position if (self.body) else self.position
        window.blit(surface, surface.get_rect(center=position))
