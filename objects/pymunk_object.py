import pymunk as pm
import pygame as pg
import math


class PymunkObject:
    surface:pg.Surface
    body:pm.Body|None = None
    shape:pm.Shape
    position:tuple[int, int]

    def __init__(self, id:int, mass:float=10.0, friction:float=0.5, elasticity:float=0.5, body_type:int=pm.Body.DYNAMIC, group_id:int=0):
        self.id = id
        self.mass = mass
        self.friction = friction
        self.elasticity = elasticity
        self.body_type = body_type
        self.z_index = 0
        self.group_id = group_id
    
    def properties(self) -> dict:
        return {'mass':self.mass, 'friction':self.friction, 'elasticity':self.elasticity}
    
    def place(self, space:pm.Space) -> None:
        self.body = pm.Body(body_type=self.body_type)
        self.body.position = self.position
    
    def move_front(self):
        self.z_index += 1
        print(self.z_index)
    
    def move_back(self):
        self.z_index -= 1
        print(self.z_index)
    
    def clicked(self, event:pg.event.Event, consumed:list, space:pm.Space) -> tuple[float, float]:
        if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and event not in consumed):
            hits = space.point_query(pm.Vec2d(*event.pos), 0, pm.ShapeFilter())
            if (hits):
                if (self.shape in list(map(lambda hit: hit.shape, hits))):
                    consumed.append(event)
                    return self.body.world_to_local(event.pos)
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
            'body_type':self.body_type,
            'z_index':self.z_index,
            'group_id':self.group_id
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
        surface = pg.transform.rotate(self.surface, math.degrees(self.body.angle) * -1)
        position = self.body.position
        window.blit(surface, surface.get_rect(center=position))
