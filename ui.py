import pygame as pg
from settings import FONTS
from typing import Callable

class ButtonBehavior:
    def __init__(self, left:float, top:float, width:float, height:float, on_press:Callable|None):
        self.rect = pg.Rect(left, top, width, height)
        self.clickable:bool = True
        self.on_press = on_press
    
    def clicked(self, event:pg.event.Event, consumed:list) -> bool:
        if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and event not in consumed):
            if (self.rect.collidepoint(pg.mouse.get_pos()) and self.clickable):
                if (self.on_press):
                    self.on_press()
                consumed.append(event)
                return True
        return False

class ImageButton(ButtonBehavior):
    def __init__(self, left:float, top:float, width:float, height:float, on_press:Callable, image:pg.Surface):
        super().__init__(left, top, width, height, on_press)
        self.image = image
    
    def draw(self, window:pg.Surface) -> None:
        window.blit(self.image, self.rect)


class TextButton(ButtonBehavior):
    def __init__(self, left: float, top: float, width: float, height: float, on_press: Callable, background_color:tuple[int, int, int], content:str, size:str='large'):
        super().__init__(left, top, width, height, on_press)
        self.surface = pg.Surface((width, height), pg.SRCALPHA)
        self.surface.fill((0, 0, 0, 100))
        self.background_color = background_color
        self.content = content
        self.size = size
    
    def get_text(self) -> tuple[pg.Surface, pg.Rect]:
        text = FONTS.get(self.size).render(self.content, True, (0, 0, 0))
        return (text, text.get_rect(center=self.rect.center))
    
    def draw(self, window:pg.Surface) -> None:
        pg.draw.rect(window, self.background_color, self.rect)
        if (not self.clickable):
            window.blit(self.surface, self.rect)
        if (self.content):
            text, rect = self.get_text()
            window.blit(text, rect)

class ToolButton(TextButton):
    def __init__(self, left:float, top:float, width:float, height:float, on_press:Callable, background_color:tuple[int, int, int], content:str=''):
        super().__init__(left, top, width, height, on_press, background_color, content)
    
    def get_text(self) -> tuple[pg.Surface, pg.Rect]:
        text = FONTS.get('small').render(self.content, True, (0, 0, 0))
        return (text, text.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 5)))