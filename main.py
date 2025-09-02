import pymunk as pm
import pygame as pg
import pymunk.pygame_util
pg.init()
from constraints.damped_spring import DampedSpring
from constraints.pin_joint import PinJoint
from constraints.gear_joint import GearJoint
from constraints.constraint import PymunkConstraint
from objects.pymunk_object import PymunkObject
from objects.circle import Circle
from objects.rectangle import Rectangle
from objects.square import Square
from objects.pin import Pin
from ui import ToolButton, TextButton, ToggleButton, DropMenu
from tk_dialogues import EditMenu
from mouse import Mouse
import math
import pickle
from tkinter import filedialog
import commands

reset_click = pg.USEREVENT + 1


class Simulation:
    running:bool = True
    objects:list = []
    tool:str = None
    placeholder:tuple[int, int] = None
    constraints:list = []
    pins:list[Pin] = []
    playing:bool = False
    selected_object:PymunkObject = None
    selected_constraint:PymunkConstraint = None
    current_constraint:PymunkConstraint = None
    clicked = False
    file:str = None
    offset:tuple[int, int] = None
    default_collide = True
    ctrl = False
    shift = False
    group_select = []
    group = 0
    id = 0

    def __init__(self):
        self.window = pg.display.set_mode((1440, 900), flags=pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.space = pm.Space()
        self.mouse = Mouse()
        self.space.gravity = (0, 981)
        self.commands:commands.Tools = commands.Tools(self)
        self.buttons = {
            'move_front':TextButton(150, 0, 70, 25, lambda: self.selected_object.move_front(), (255, 255, 0), 'Move Front', 'small'),
            'move_back':TextButton(230, 0, 70, 25, lambda: self.selected_object.move_back(), (255, 255, 0), 'Move Back', 'small'),
            'not_collide':TextButton(310, 0, 100, 25, self.commands.not_collide, (0, 255, 255), 'Not Collide', 'small'),
            'collide': TextButton(420, 0, 100, 25, self.commands.collide, (0, 255, 255), 'Collide', 'small'),
            'toggle_collision': ToggleButton(530, 0, 100, 25, lambda down: setattr(self, 'default_collide', not down), (0, 255, 255), ('Colliding', 'Not Colliding'), 'small'),
            'circle':ToolButton(10, 35, 50, 50, lambda: self.commands.changeTool('Circle'), (255, 0, 0), 'Circle'), 
            'square':ToolButton(70, 35, 50, 50, lambda: self.commands.changeTool('Square'), (0, 255, 0), 'Square'),
            'rectangle':ToolButton(130, 35, 50, 50, lambda: self.commands.changeTool('Rectangle'), (0, 0, 255), 'Rectangle'), 
            'move':ToolButton(130, 115, 50, 50, lambda: self.commands.changeTool('Move'), (0, 0, 255), 'Move'),
            'spring':ToolButton(10, 115, 50, 50, lambda: self.commands.changeTool('Spring'), (255, 0, 255), 'Spring'),
            'pinJoint':ToolButton(10, 195, 50, 50, lambda: self.commands.changeTool('PinJoint'), (255, 255, 0), 'PinJoint'),
            'anchor':ToolButton(70, 115, 50, 50, lambda: self.commands.changeTool('Anchor'), (0, 255, 255), 'Anchor'),
            'gearJoint': ToolButton(130, 195, 50, 50, lambda: self.commands.changeTool('GearJoint'), (255, 0, 0), 'GearJoint'),
            'pivotJoint': ToolButton(70, 195, 50, 50, lambda: self.commands.changeTool('PivotJoint'), (0, 255, 0), 'PivotJoint'),
            'pin':ToolButton(10, 275, 50, 50, lambda: self.commands.changeTool('Pin'), (0, 255, 0), 'Pin'),
            'start':TextButton(10, 820, 340, 70, self.commands.start, (255, 255, 0), 'Start'), 
            'pause':TextButton(10, 740, 340, 70, self.commands.pause, (255, 0, 255), 'Pause'),
            'clear':TextButton(10, 660, 340, 70, self.commands.clear, (0, 255, 255), 'Clear')
        }
        self.drop_menus = {
            'file':DropMenu(0, 0, 70, 25, ['New', 'Load', 'Save As', 'Save'], self.commands.file_select, (200, 200, 200), 'File'),
            'edit':DropMenu(70, 0, 70, 25, ['Undo', 'Redo', 'Delete'], self.commands.edit_select, (200, 200, 200), 'Edit')
        }
        self.border_shapes = []
        self.options = pymunk.pygame_util.DrawOptions(self.window)
        self.options.flags = pymunk.pygame_util.DrawOptions.DRAW_CONSTRAINTS
        h = self.space.add_collision_handler(1, 1)
        h.begin = self.only_collide_same
        self.create_border(360, 25)
        self.loop()
    
    def only_collide_same(self, arbiter, space, data):
        a, b = arbiter.shapes
        return a.group_id != b.group_id
    
    def create_border(self, x, y):
        for border_shape in self.border_shapes:
            if (border_shape in self.space.shapes):
                self.space.remove(border_shape)
        self.border_shapes.clear()
        self.borders = [
            [(x, self.window.get_height()-10), (self.window.get_width(), self.window.get_height()-10), (self.window.get_width(), self.window.get_height()), (x, self.window.get_height())], 
            [(x, y), (self.window.get_width(), y), (self.window.get_width(), y+10), (x, y+10)],
            [(x, y), (x, self.window.get_height()), (x+10, self.window.get_height()), (x+10, y)], 
            [(self.window.get_width()-10, y), (self.window.get_width()-10, self.window.get_height()), (self.window.get_width(), self.window.get_height()), (self.window.get_width(), y)]
            ]
        for border in self.borders:
            borderShape = pm.shapes.Poly(self.space.static_body, border)
            borderShape.friction = 0.5
            borderShape.elasticity = 0.5
            self.border_shapes.append(borderShape)
            self.space.add(borderShape)
    
    def loop(self):
        while (self.running):
            self.objects.sort(key=lambda x: x.z_index)
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    pg.quit()
                    quit()
                if (event.type == pg.VIDEORESIZE):
                    self.create_border(360, 25)
                if (event.type == reset_click):
                    self.clicked = False
                if (event.type == pg.KEYDOWN):
                    if (event.key == pg.K_LCTRL or event.key == pg.K_RCTRL):
                        self.ctrl = True
                    elif (event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT):
                        self.shift = True
                    else:
                        for shortcut, func in self.commands.shorcuts.items():
                            if (shortcut == 'delete' and event.key == pg.K_DELETE):
                                func()
                            elif ('ctrl' in shortcut and self.ctrl):
                                if ('shift' in shortcut and not self.shift):
                                    continue
                                if (pg.key.name(event.key) in shortcut):
                                    func()
                if (event.type == pg.KEYUP):
                    if (event.key == pg.K_LCTRL or event.key == pg.K_RCTRL):
                        self.ctrl = False
                    if (event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT):
                        self.shift = False
                if (event.type == pg.USEREVENT + 2):
                    for key, value in event.dict.items():
                        if (self.selected_object):
                            setattr(self.selected_object, key, float(value))
                            setattr(self.selected_object.body, key, float(value))
                        if (self.selected_constraint):
                            setattr(self.selected_constraint, key, float(value))
                            setattr(self.selected_constraint.constraint, key, float(value))
                
                for pin in self.pins:
                    pin.hover(event)
                    
                consumed = []
                for drop_menu in self.drop_menus.values():
                    drop_menu.handle(event, consumed)

                for button in self.buttons.values():
                    button.clicked(event, consumed)
                
                self.mouse.move(event)
                if (self.tool in ['Circle', 'Rectangle', 'Square'] and not self.playing):
                    if (self.mouse.down(event, consumed)):
                        if (1430 >= self.mouse.position[0] >= 370 and 890 >= self.mouse.position[1] >= 10):
                            self.placeholder = self.mouse.position
                            break
                    if (self.mouse.up(event, consumed)):
                        if (self.placeholder):
                            pymunkObject = None
                            if (self.tool == 'Circle'):
                                pymunkObject = Circle(self.id, self.placeholder, math.dist(self.placeholder, self.mouse.position), group_id=self.group)
                            elif (self.tool == 'Rectangle'):
                                pymunkObject = Rectangle(self.id, self.placeholder, self.mouse.position, group_id=self.group)
                            elif (self.tool == 'Square'):
                                pymunkObject = Square(self.id, self.placeholder, self.mouse.position, group_id=self.group)
                            if (pymunkObject):
                                pymunkObject.place(self.space)
                                self.objects.append(pymunkObject)
                                self.id += 1
                                if (self.default_collide):
                                    self.group += 1
                            self.placeholder = None
                            self.commands.record()
                            break
                
                #Handles constraint selection and interaction
                for constraint in self.constraints:
                    if (not self.tool):
                        if (constraint.clicked(event, consumed)):
                            self.selected_constraint = constraint
                            # If the tool is not set, open the edit menu
                            if (not self.tool and not self.playing):
                                if (self.clicked):
                                    properties = self.selected_constraint.properties()
                                    if (properties):
                                        EditMenu(properties)
                                self.clicked = True
                                pg.time.set_timer(reset_click, 500, 1)
                            break
                
                # Handles object selection and interaction
                offset = None
                for obj in sorted(self.objects, key=lambda obj: obj.z_index, reverse=True):
                    offset = obj.clicked(event, consumed, self.space)
                    if (offset):
                        self.selected_object = obj
                        for pin in filter(lambda p: p.body == self.selected_object, self.pins):
                            if (pin.clicked(event)):
                                offset = pin.offset
                                break
                        # Add to group selection if ctrl is pressed
                        if (self.ctrl):
                            self.group_select.append(self.selected_object)
                        # Selects the objects for movement 
                        if (self.tool == 'Move' and not self.playing):
                            self.offset = offset
                            self.mouse.hold = True
                        # Add constraints to the selected object
                        elif (self.tool in ['Spring', 'PinJoint', 'GearJoint'] and not self.playing):
                            if (not self.current_constraint):
                                if (self.tool == 'Spring'):
                                    self.current_constraint = DampedSpring(self.selected_object, offset)
                                elif (self.tool == 'PinJoint'):
                                    self.current_constraint = PinJoint(self.selected_object, offset)
                                elif (self.tool == 'GearJoint'):
                                    self.current_constraint = GearJoint(self.selected_object, offset)
                            else:
                                if (self.selected_object != self.current_constraint.body_a):
                                    self.current_constraint.set_body_b(self.selected_object, offset)
                                    self.constraints.append(self.current_constraint)
                                    self.current_constraint.place(self.space)
                                    self.commands.record()
                                self.current_constraint = None
                        # Anchor the selected object
                        elif (self.tool == 'Anchor' and not self.playing):
                            self.selected_object.body.body_type = pm.Body.STATIC
                            self.commands.record()
                        elif (self.tool == 'Pin' and not self.playing):
                            pin = Pin(self.selected_object, offset)
                            self.pins.append(pin)
                            self.commands.record()
                        # If the tool is not set, open the edit menu
                        if (not self.tool and not self.playing):
                            if (self.clicked):
                                EditMenu(self.selected_object.properties())
                            self.clicked = True
                            pg.time.set_timer(reset_click, 500, 1)
                        break
                
                # If no object was clicked, reset the selected object
                if (not self.tool and not offset and event.type == pg.MOUSEBUTTONDOWN and event not in consumed):
                    self.selected_object = None
                    self.group_select.clear()

                # Moving objects around the space
                if (self.tool == 'Move' and not self.playing):
                    if (self.selected_object and self.mouse.dragging(event)):
                        position = (self.mouse.position[0] - self.offset[0], self.mouse.position[1] - self.offset[1])
                        self.selected_object.set_position(position)
                        self.space.reindex_shapes_for_body(self.selected_object.body)
                    if (self.mouse.up(event, consumed)):
                        for constraint in self.constraints:
                            if constraint.body_a == self.selected_object or constraint.body_b == self.selected_object:
                                constraint.remove(self.space)
                                constraint.place(self.space)
                        self.selected_object = None
                
                # Adding constraints on the space
                if (self.tool in ['Spring', 'PinJoint'] and not self.playing):
                    if (not offset and self.mouse.down(event, consumed)):
                        if (not self.current_constraint):
                            if (self.tool == 'Spring'):
                                self.current_constraint = DampedSpring(self.space.static_body, self.mouse.position)
                            elif (self.tool == 'PinJoint'):
                                self.current_constraint = PinJoint(self.space.static_body, self.mouse.position)
                        else:
                            if (self.current_constraint.body_a != self.space.static_body):
                                self.current_constraint.set_body_b(self.space.static_body, self.mouse.position)
                                self.constraints.append(self.current_constraint)
                                self.current_constraint.place(self.space)
                                self.commands.record()
                            self.current_constraint = None

                # Interacting with the objects using the mouse
                if (self.playing):
                    for obj in self.objects:
                        offset = obj.clicked(event, consumed, self.space)
                        if (offset):
                            offset = (-1*offset[0], -1*offset[1])
                            self.mouse.join(obj.body, offset, self.space)
                            break
                    if (event.type == pg.MOUSEBUTTONUP and self.mouse.joint):
                        self.mouse.unjoin(self.space)
            
            if (not self.playing):
                self.buttons.get('move_front').clickable = self.selected_object is not None
                self.buttons.get('move_back').clickable = self.selected_object is not None
                self.buttons.get('not_collide').clickable = len(self.group_select) > 0
                self.buttons.get('collide').clickable = len(self.group_select) > 0
            
            self.draw()
            self.clock.tick(60)
            if (self.playing):
                self.space.step(1/60)
    
    def draw(self):
        self.window.fill((255, 255, 255))

        for border in self.borders:
            pg.draw.polygon(self.window, (0, 0, 0), border)

        for button in self.buttons.values():
            button.draw(self.window)
            if (isinstance(button, ToolButton)):
                if (button.content == self.tool):
                    pg.draw.rect(self.window, (0, 0, 0), button.rect, width=2)
        
        for drop_menu in self.drop_menus.values():
            drop_menu.draw(self.window)

        if (self.placeholder):
            if (self.tool == 'Circle'):
                pg.draw.circle(self.window, (255, 0, 0), self.placeholder, math.dist(self.placeholder, self.mouse.position))
            elif (self.tool == 'Rectangle'):
                width = abs(self.placeholder[0] - self.mouse.position[0])
                height = abs(self.placeholder[1] - self.mouse.position[1])
                pg.draw.rect(self.window, (255, 0, 0), (self.placeholder[0], self.placeholder[1], width, height))
            elif (self.tool == 'Square'):
                side = (math.dist(self.placeholder, self.mouse.position) * math.sqrt(2))/2
                pg.draw.rect(self.window, (0, 0, 255), (self.placeholder[0], self.placeholder[1], side, side))
        
        for object in self.objects:
            object.draw(self.window)
        
        for pin in self.pins:
            pin.draw(self.window)
        
        self.space.debug_draw(self.options)
        pg.display.update()


if __name__ == '__main__':
    simulation = Simulation()

