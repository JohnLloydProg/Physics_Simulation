import pygame as pg
import pymunk as pm


class Mouse:
    hold = False
    position = (0, 0)
    body = pm.Body(body_type=pm.Body.KINEMATIC)
    joint = None

    def down(self, event:pg.event.Event, consumed:list) -> bool:
        if (event.type == pg.MOUSEBUTTONDOWN and event not in consumed):
            self.hold = True
            return True
        return False

    def up(self, event:pg.event.Event, consumed:list) -> bool:
        if (event.type == pg.MOUSEBUTTONUP and event not in consumed):
            self.hold = False
            return True
        return False

    def move(self, event:pg.event.Event) -> bool:
        if (event.type == pg.MOUSEMOTION):
            self.position = pg.mouse.get_pos()
            self.body.position = self.position
            return True
        return False

    def dragging(self, event:pg.event.Event) -> bool:
        return (self.move(event) and self.hold)

    def join(self, body, offset, space:pm.Space):
        self.joint = pm.PivotJoint(self.body, body, (0, 0), offset)
        self.joint.max_force = 50000
        self.joint.error_bias = (1 - 0.15) ** 60
        space.add(self.joint)
    
    def unjoin(self, space:pm.Space):
        space.remove(self.joint)
        self.joint = None

