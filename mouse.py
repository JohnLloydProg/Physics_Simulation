import pygame as pg


class Mouse:
    hold = False
    position = (0, 0)

    def down(self, event:pg.event.Event) -> bool:
        if (event.type == pg.MOUSEBUTTONDOWN):
            self.hold = True
            return True
        return False

    def up(self, event:pg.event.Event) -> bool:
        if (event.type == pg.MOUSEBUTTONUP):
            self.hold = False
            return True
        return False

    def move(self, event:pg.event.Event) -> bool:
        if (event.type == pg.MOUSEMOTION):
            self.position = pg.mouse.get_pos()
            return True
        return False

    def dragging(self, event:pg.event.Event) -> bool:
        return (self.move(event) and self.hold)

