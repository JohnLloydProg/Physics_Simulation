import pymunk as pm
import pygame as pg
import math


class PymunkObject:
    surface:pg.Surface
    body:pm.Body|None = None
    shape:pm.Shape
    position:tuple[int, int]

    def __init__(self, mass:float=10.0, friction:float=0.5, elasticity:float=0.5, body_type:int=pm.Body.DYNAMIC):
        self.mass = mass
        self.friction = friction
        self.elasticity = elasticity
        self.body_type = body_type
    
    def place(self, space:pm.Space) -> None:
        self.body = pm.Body(body_type=self.body_type)
        self.body.position = self.position
    
    def clicked(self, event:pg.event.Event) -> bool:
        if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1):
            surface = pg.transform.rotate(self.surface, math.degrees(self.body.angle) * -1) if (self.body) else self.surface
            position = self.body.position if (self.body) else self.position
            rect = surface.get_rect(center=position)
            if (rect.collidepoint(event.pos)):
                cursor_mask = pg.Mask((3, 3), True)
                mask = pg.mask.from_surface(surface)
                if (mask.overlap(cursor_mask, (event.pos[0] - rect.x, event.pos[1] - rect.y))):
                    return True
        return False
    
    def remove(self, space:pm.Space) -> None:
        if (self.body):
            space.remove(self.body, self.shape)
            self.body = None
    
    def draw(self, window:pg.Surface) -> None:
        surface = pg.transform.rotate(self.surface, math.degrees(self.body.angle) * -1) if (self.body) else self.surface
        position = self.body.position if (self.body) else self.position
        window.blit(surface, surface.get_rect(center=position))
