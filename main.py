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
from ui import ToolButton, TextButton
from tk_dialogues import EditMenu
from mouse import Mouse
import math
import pickle
from tkinter import filedialog

reset_click = pg.USEREVENT + 1


class Simulation:
    running:bool = True
    objects:list = []
    tool:str = None
    placeholder:tuple[int, int] = None
    constraints:list = []
    playing:bool = False
    selected_object:PymunkObject = None
    selected_constraint:PymunkConstraint = None
    current_constraint:PymunkConstraint = None
    clicked = False
    file:str = None
    offset:tuple[int, int] = None
    ctrl = False
    group_select = []
    group = 0
    id = 0

    def __init__(self):
        self.window = pg.display.set_mode((1440, 900), flags=pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.space = pm.Space()
        self.mouse = Mouse()
        self.space.gravity = (0, 981)
        self.commands = Tools(self)
        self.buttons = {
            'undo':TextButton(540, 0, 50, 25, lambda: self.commands.undo(), (255, 0, 0), 'Undo', 'small'),
            'redo':TextButton(600, 0, 50, 25, lambda: self.commands.redo(), (255, 0, 0), 'Redo', 'small'),
            'save_as': TextButton(360, 0, 50, 25, lambda: self.commands.save(), (0, 0, 255), 'Save As', 'small'),
            'save':TextButton(420, 0, 50, 25, lambda: self.commands.save(self.file), (0, 255, 0), 'Save', 'small'),
            'load':TextButton(480, 0, 50, 25, lambda: self.commands.load(), (0, 255, 0), 'Load', 'small'),
            'delete':TextButton(660, 0, 50, 25, lambda: self.commands.delete(), (255, 0, 0), 'Delete', 'small'),
            'move_front':TextButton(730, 0, 60, 25, lambda: self.selected_object.move_front(), (255, 255, 0), 'Move Front', 'small'),
            'move_back':TextButton(800, 0, 60, 25, lambda: self.selected_object.move_back(), (255, 255, 0), 'Move Back', 'small'),
            'not_collide':TextButton(870, 0, 100, 25, lambda: self.commands.not_collide(), (0, 255, 255), 'Not Collide', 'small'),
            'circle':ToolButton(10, 10, 50, 50, lambda: self.commands.changeTool('Circle'), (255, 0, 0), 'Circle'), 
            'square':ToolButton(70, 10, 50, 50, lambda: self.commands.changeTool('Square'), (0, 255, 0), 'Square'),
            'rectangle':ToolButton(130, 10, 50, 50, lambda: self.commands.changeTool('Rectangle'), (0, 0, 255), 'Rectangle'), 
            'move':ToolButton(130, 90, 50, 50, lambda: self.commands.changeTool('Move'), (0, 0, 255), 'Move'),
            'spring':ToolButton(10, 90, 50, 50, lambda: self.commands.changeTool('Spring'), (255, 0, 255), 'Spring'),
            'pinJoint':ToolButton(10, 170, 50, 50, lambda: self.commands.changeTool('PinJoint'), (255, 255, 0), 'PinJoint'),
            'anchor':ToolButton(70, 90, 50, 50, lambda: self.commands.changeTool('Anchor'), (0, 255, 255), 'Anchor'),
            'gearJoint': ToolButton(130, 90, 50, 50, lambda: self.commands.changeTool('GearJoint'), (255, 0, 0), 'GearJoint'),
            'start':TextButton(10, 820, 340, 70, self.commands.start, (255, 255, 0), 'Start'), 
            'pause':TextButton(10, 740, 340, 70, self.commands.pause, (255, 0, 255), 'Pause'),
            'clear':TextButton(10, 660, 340, 70, self.commands.clear, (0, 255, 255), 'Clear')
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
                if (event.type == pg.KEYUP):
                    if (event.key == pg.K_LCTRL or event.key == pg.K_RCTRL):
                        self.ctrl = False
                if (event.type == pg.USEREVENT + 2):
                    for key, value in event.dict.items():
                        if (self.selected_object):
                            setattr(self.selected_object, key, float(value))
                            setattr(self.selected_object.body, key, float(value))
                        if (self.selected_constraint):
                            setattr(self.selected_constraint, key, float(value))
                            setattr(self.selected_constraint.constraint, key, float(value))
                    
                consumed = []
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
                                pymunkObject = Rectangle(self.id, self.placeholder, self.mouse.position)
                            elif (self.tool == 'Square'):
                                pymunkObject = Square(self.id, self.placeholder, self.mouse.position)
                            if (pymunkObject):
                                pymunkObject.place(self.space)
                                self.objects.append(pymunkObject)
                                self.id += 1
                                self.group += 1
                            self.placeholder = None
                            self.commands.record()
                            break

                for constraint in self.constraints:
                    if (constraint.clicked(event, consumed)):
                        self.selected_constraint = constraint
                        if (not self.tool and not self.playing):
                            if (self.clicked):
                                EditMenu(self.selected_constraint.properties())
                            self.clicked = True
                            pg.time.set_timer(reset_click, 500, 1)
                        break

                offset = None
                for obj in sorted(self.objects, key=lambda obj: obj.z_index, reverse=True):
                    offset = obj.clicked(event, consumed, self.space)
                    if (offset):
                        self.selected_object = obj
                        if (self.ctrl):
                            self.group_select.append(self.selected_object)
                            print(self.group_select)
                        if (self.tool == 'Move' and not self.playing):
                            self.offset = offset
                            self.mouse.hold = True
                        elif (self.tool in ['Spring', 'PinJoint'] and not self.playing):
                            offset = (-1*offset[0], -1*offset[1])
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
                        elif (self.tool == 'Anchor' and not self.playing):
                            self.selected_object.body.body_type = pm.Body.STATIC
                        if (not self.tool and not self.playing):
                            if (self.clicked):
                                EditMenu(self.selected_object.properties())
                            self.clicked = True
                            pg.time.set_timer(reset_click, 500, 1)
                        break
                if (not self.tool and not offset and event.type == pg.MOUSEBUTTONDOWN and event not in consumed):
                    self.selected_object = None
                    self.group_select.clear()
                            

                if (self.tool == 'Move' and not self.playing):
                    if (self.selected_object and self.mouse.dragging(event)):
                        position = (self.mouse.position[0] + self.offset[0], self.mouse.position[1] + self.offset[1])
                        self.selected_object.set_position(position)
                        self.space.reindex_shapes_for_body(self.selected_object.body)
                    if (self.mouse.up(event, consumed)):
                        for constraint in self.constraints:
                            if constraint.body_a == self.selected_object or constraint.body_b == self.selected_object:
                                constraint.remove(self.space)
                                constraint.place(self.space)
                        self.selected_object = None

                if (self.tool in ['Spring', 'PinJoint'] and not self.playing):
                    if (not offset and self.mouse.down(event, consumed)):
                        if (not self.current_constraint):
                            if (self.tool == 'Spring'):
                                self.current_constraint = DampedSpring(self.space.static_body, self.mouse.position)
                            elif (self.tool == 'PinJoint'):
                                self.current_constraint = PinJoint(self.space.static_body, self.mouse.position)
                            elif (self.tool == 'GearJoint'):
                                self.current_constraint = GearJoint(self.space.static_body, self.mouse.position)
                        else:
                            if (self.current_constraint.body_a != self.space.static_body):
                                self.current_constraint.set_body_b(self.space.static_body, self.mouse.position)
                                self.constraints.append(self.current_constraint)
                                self.current_constraint.place(self.space)
                                self.commands.record()
                            self.current_constraint = None

                if (self.playing):
                    for obj in self.objects:
                        offset = obj.clicked(event, consumed, self.space)
                        if (offset):
                            offset = (-1*offset[0], -1*offset[1])
                            self.mouse.join(obj.body, offset, self.space)
                            break
                    if (event.type == pg.MOUSEBUTTONUP and self.mouse.joint):
                        self.mouse.unjoin(self.space)
                    
            
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
        
        self.space.debug_draw(self.options)
        pg.display.update()


class Tools:
    undoStack = []
    redoStack = []

    def __init__(self, simulation:Simulation):
        self.simulation = simulation
        self.undoStack = [self.encrypt()]
    
    def delete(self):
        if (self.simulation.selected_object and not self.simulation.tool):
            self.simulation.selected_object.remove(self.simulation.space)
            self.simulation.objects.remove(self.simulation.selected_object)
            for constraint in self.simulation.constraints:
                if  constraint.body_a == self.simulation.selected_object or constraint.body_b == self.simulation.selected_object:
                    constraint.remove(self.simulation.space)
                    self.simulation.constraints.remove(constraint)

    
    def changeTool(self, tool):
        if (tool != self.simulation.tool):
            self.simulation.tool = tool
        else:
            self.simulation.tool = None
        print(self.simulation.tool)
    
    def start(self):
        if (self.simulation.playing):
            for object in self.simulation.objects:
                object.reset()
                self.simulation.space.reindex_shapes_for_body(object.body)
        
        for button in self.simulation.buttons.values():
            if (isinstance(button, ToolButton)):
                button.clickable = not button.clickable
        clear_btn:ToolButton = self.simulation.buttons.get('clear')
        clear_btn.clickable = not clear_btn.clickable
        self.simulation.playing = not self.simulation.playing
        self.simulation.tool = None
    
    def pause(self):
        self.simulation.playing = not self.simulation.playing
        self.simulation.tool = None
    
    def load(self):
        try:
            asked_file = filedialog.askopenfilename(filetypes=[('Physics Files', '*.phys')])
            with open(asked_file, 'rb') as f:
                read_data = f.read()
            self.simulation.file = asked_file
            pg.display.set_caption(asked_file)
        except FileNotFoundError as e:
            print(e)
            return
        
        print('loadinggg')
        self.simulation.objects = self.decrypt(read_data)

    def save(self, file:str=''):
        asked_file = filedialog.asksaveasfilename(filetypes=[('Physics Files', '*.phys')]) if not file else file
        file_names = asked_file.split('.')
        if (len(file_names) > 1):
            asked_file = file_names.pop(0)
        data = self.encrypt()
        
        try:
            with open(f'{asked_file}.phys', 'rb') as f:
                read_data = f.read()
            if (read_data != data):
                print('saving')
                with open(f'{asked_file}.phys', 'wb') as f:
                    f.write(data)
        except FileNotFoundError as e:
            print('creating file')
            with open(f'{asked_file}.phys', 'wb') as f:
                f.write(data)
            self.simulation.file = asked_file
            pg.display.set_caption(asked_file)
        

    def undo(self):
        if (len(self.undoStack) > 1):
            action = self.undoStack.pop()
            self.redoStack.append(action)
            self.clear()
            data = self.decrypt(self.undoStack[-1])
            self.simulation.objects = data.get('objects', [])
            self.simulation.constraints = data.get('constraints', [])
        self.simulation.tool = None
    
    def redo(self):
        if (self.redoStack):
            action = self.redoStack.pop()
            self.undoStack.append(action)
            self.clear()
            data = self.decrypt(self.undoStack[-1])
            self.simulation.objects = data.get('objects', [])
            self.simulation.constraints = data.get('constraints', [])
        self.simulation.tool = None
    
    def record(self):
        self.undoStack.append(self.encrypt())
        self.redoStack.clear()

    def encrypt(self):
        data = {'objects': [], 'constraints': []}
        for pymunkObject in self.simulation.objects:
            data['objects'].append(pymunkObject.json())
        for pymunkConstraint in self.simulation.constraints:
            data['constraints'].append(pymunkConstraint.json())
        return pickle.dumps(data)
    
    def decrypt(self, data):
        data = pickle.loads(data)
        jsonObjects = data.get('objects')
        jsonConstraints = data.get('constraints')
        returnedData = {'objects':[], 'constraints':[]}
        pymunk_objects:dict[str, PymunkObject] = {'Circle':Circle, 'Rectangle':Rectangle, 'Square':Square}
        pymunk_constraints:dict[str, PymunkConstraint] = {'DampedSpring':DampedSpring, 'PinJoint':PinJoint}
        for jsonObject in jsonObjects:
            pymunkObject = pymunk_objects.get(jsonObject.get('type')).from_json(jsonObject)
            if (pymunkObject):
                pymunkObject.place(self.simulation.space)
                returnedData['objects'].append(pymunkObject)
        for jsonConstraint in jsonConstraints:
            pymunkConstraint = pymunk_constraints.get(jsonConstraint.get('type')).from_json(jsonConstraint, self.simulation.space, returnedData['objects'])
            if (pymunkConstraint):
                pymunkConstraint.place(self.simulation.space)
                returnedData['constraints'].append(pymunkConstraint)
        return returnedData

    def clear(self):
        for constraint in self.simulation.constraints:
            constraint.remove(self.simulation.space)

        for object in self.simulation.objects:
            object.remove(self.simulation.space)
        self.simulation.objects.clear()
        self.simulation.playing = False
        self.simulation.tool = None
    
    def not_collide(self):
        for obj in self.simulation.group_select:
            obj.group_id = self.simulation.group
            obj.shape.group_id = self.simulation.group
        self.simulation.group += 1



if __name__ == '__main__':
    simulation = Simulation()

