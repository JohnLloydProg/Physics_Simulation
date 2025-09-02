import pygame as pg
import pymunk as pm
from objects.pymunk_object import PymunkObject
import math


class Pin:
    def __init__(self, body:PymunkObject|pm.Body, offset:tuple[float, float]):
        self.body = body
        self.offset = offset
        self.inside = False
    
    def world_position(self) -> tuple[float, float]:
        body = self.body.body if (isinstance(self.body, PymunkObject)) else self.body

        return body.local_to_world(self.offset)
    
    def hover(self, event:pg.event.Event) -> bool:
        if (event.type == pg.MOUSEMOTION):
            position = self.world_position()
            self.inside = math.dist(position, event.pos) < 5
    
    def clicked(self, event:pg.event.Event) -> bool:
        if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1):
            return self.inside
        return False

    def json(self) -> dict:
        data = {
            'body': self.body.id if (isinstance(self.body, PymunkObject)) else 'space',
            'offset': self.offset
        }
        return data

    @staticmethod
    def from_json(data:dict, space:pm.Space, objects:list) -> 'Pin':
        if data['body'] == 'space':
            body = space.static_body
        else:
            for pymunk_object in objects:
                if (isinstance(pymunk_object, PymunkObject) and pymunk_object.id == data['body']):
                    body = pymunk_object
                    break
        return Pin(body=body, offsset=data['offset'])

    def draw(self, window:pg.Surface) -> None:
        position = self.world_position()
        pg.draw.circle(window, (130, 130, 130), (int(position[0]), int(position[1])), 5)
        pg.draw.circle(window, (0, 0, 0) if not self.inside else (0, 255, 0), (int(position[0]), int(position[1])), 5, 2)
