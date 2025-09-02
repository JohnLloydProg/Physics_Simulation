import pygame as pg
import pymunk as pm 
from objects.pymunk_object import PymunkObject
import math


class PymunkConstraint:
    constraint:pm.Constraint
    body_b: pm.Body = None

    def __init__(self, body_a: PymunkObject|pm.Body, anchor_a: tuple[float, float]):
        self.body_a = body_a
        self.anchor_a = anchor_a
        self.constraint = None

    def properties(self) -> dict:
        return {}
    
    def set_body_b(self, body_b: PymunkObject|pm.Body, anchor_b: tuple[float, float]) -> None:
        self.body_b = body_b
        self.anchor_b = anchor_b
    
    def clicked(self, event, consumed:list):
        if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and event not in consumed):
            body_a:pm.Body = self.body_a.body if (isinstance(self.body_a, PymunkObject)) else self.body_a
            body_b:pm.Body = self.body_b.body if (isinstance(self.body_b, PymunkObject)) else self.body_b
            p1 = body_a.local_to_world(self.anchor_a)
            p2 = body_b.local_to_world(self.anchor_b)
            width = math.dist(p1 ,p2)
            rise = p1[1] - p2[1]
            run = p1[0] - p2[0]
            try:
                angle = math.degrees(math.atan(abs(rise) / abs(run)))
            except ZeroDivisionError:
                angle = 90
            surface = pg.Surface((width+20, 20), pg.SRCALPHA)
            surface.fill((255, 0, 0))
            surface = pg.transform.rotate(surface, angle * (1 if rise * run < 0 else -1))
            position = (int((p1[0] + p2[0])/2), int((p1[1] + p2[1])/2))
            rect = surface.get_rect(center=position)
            if (rect.collidepoint(event.pos)):
                cursor_mask = pg.Mask((3, 3), True)
                mask = pg.mask.from_surface(surface)
                if (mask.overlap(cursor_mask, (event.pos[0] - rect.x, event.pos[1] - rect.y))):
                    consumed.append(event)
                    return True
        return False
    
    def json(self) -> dict:
        data = {
            'body_a': self.body_a.id if (isinstance(self.body_a, PymunkObject)) else 'space',
            'anchor_a': self.anchor_a,
            'body_b': self.body_b.id if (isinstance(self.body_b, PymunkObject)) else 'space',
            'anchor_b': self.anchor_b if hasattr(self, 'anchor_b') else None
        }
        return data
    
    def place(self, space:pm.Space=None) -> None:
        if (not space):
            body_a = self.body_a.body if (isinstance(self.body_a, PymunkObject)) else self.body_a
            body_b = self.body_b.body if (isinstance(self.body_b, PymunkObject)) else self.body_b
            return (body_a, body_b)

        if self.constraint:
            space.add(self.constraint)
        else:
            raise ValueError("Constraint not defined. Please define the constraint before placing it in the space.")
    
    def remove(self, space: pm.Space) -> None:
        if self.constraint:
            space.remove(self.constraint)
        else:
            raise ValueError("Constraint not defined. Please define the constraint before removing it from the space.")
    
    @staticmethod
    def from_json(data:dict, space:pm.Space, objects:list):
        if (data['body_a'] == 'space'):
            body_a = space.static_body
        else:
            for object in objects:
                if (object.id == data['body_a']):
                    body_a = object
                    break
        if (data['body_b'] == 'space'):
            body_b = space.static_body
        else:
            for object in objects:
                if (object.id == data['body_b']):
                    body_b = object
        return (body_a, body_b)
    


