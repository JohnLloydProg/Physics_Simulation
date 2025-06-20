import pymunk as pm
import pygame as pg
import pymunk.pygame_util
pg.init()
from constraints.damped_spring import DampedSpring
from constraints.constraint import PymunkConstraint
from objects.pymunk_object import PymunkObject
from objects.circle import Circle
from objects.rectangle import Rectangle
from objects.square import Square
from ui import ToolButton, TextButton
from mouse import Mouse
import math
import pickle
from tkinter import filedialog


class Simulation:
    running:bool = True
    objects:list = []
    tool:str = None
    placeholder:tuple[int, int] = None
    constraints:list = []
    playing:bool = False
    paused:bool = True
    selected_object:PymunkObject = None
    current_constraint:PymunkConstraint = None
    file:str = None
    offset:tuple[int, int] = None
    id = 0

    def __init__(self):
        self.window = pg.display.set_mode((1440, 900))
        self.clock = pg.time.Clock()
        self.space = pm.Space()
        self.mouse = Mouse()
        self.space.gravity = (0, 981)
        self.commands = Tools(self)
        self.buttons = {
            'circle':ToolButton(10, 10, 50, 50, lambda: self.commands.changeTool('Circle'), (255, 0, 0), 'Circle'), 
            'square':ToolButton(70, 10, 50, 50, lambda: self.commands.changeTool('Square'), (0, 255, 0), 'Square'),
            'rectangle':ToolButton(130, 10, 50, 50, lambda: self.commands.changeTool('Rectangle'), (0, 0, 255), 'Rectangle'), 
            'undo':ToolButton(190, 10, 50, 50, lambda: self.commands.undo(), (255, 0, 0), 'Undo'),
            'redo':ToolButton(190, 90, 50, 50, lambda: self.commands.redo(), (255, 0, 0), 'Redo'),
            'save_as': ToolButton(130, 170, 50, 50, lambda: self.commands.save(), (0, 0, 255), 'Save As'),
            'save':ToolButton(190, 170, 50, 50, lambda: self.commands.save(self.file), (0, 255, 0), 'Save'),
            'load':ToolButton(190, 250, 50, 50, lambda: self.commands.load(), (0, 255, 0), 'Load'),
            'move':ToolButton(130, 90, 50, 50, lambda: self.commands.changeTool('Move'), (0, 0, 255), 'Move'),
            'spring':ToolButton(10, 90, 50, 50, lambda: self.commands.changeTool('Spring'), (255, 0, 255), 'Spring'),
            'start':TextButton(10, 820, 340, 70, self.commands.start, (255, 255, 0), 'Start'), 
            'pause':TextButton(10, 740, 340, 70, self.commands.pause, (255, 0, 255), 'Pause'),
            'clear':TextButton(10, 660, 340, 70, self.commands.clear, (0, 255, 255), 'Clear'),
        }
        self.options = pymunk.pygame_util.DrawOptions(self.window)
        self.options.flags = pymunk.pygame_util.DrawOptions.DRAW_CONSTRAINTS
        self.create_border(360)
        self.loop()
    
    def create_border(self, x):
        self.borders = [
            [(x, 890), (x+1080, 890), (x+1080, 900), (x, 900)], [(x, 0), (x+1080, 0), (x+1080, 10), (x, 10)],
            [(x, 0), (x, 900), (x+10, 900), (x+10, 0)], [(x+1070, 0), (x+1070, 900), (x+1080, 900), (x+1080, 0)]
            ]
        for border in self.borders:
            borderShape = pm.shapes.Poly(self.space.static_body, border)
            borderShape.friction = 0.5
            borderShape.elasticity = 0.5
            self.space.add(borderShape)
    
    def loop(self):
        while (self.running):
            self.objects.sort(key=lambda x: x.z_index)
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    pg.quit()
                    quit()
                    
                consumed = []
                for button in self.buttons.values():
                    button.clicked(event, consumed)
                
                for object in self.objects:
                    object.clicked(event, consumed)
                
                self.mouse.move(event)
                if (self.tool in ['Circle', 'Rectangle', 'Square']):
                    if (self.mouse.down(event, consumed)):
                        if (1430 >= self.mouse.position[0] >= 370 and 890 >= self.mouse.position[1] >= 10):
                            self.placeholder = self.mouse.position
                            break
                    if (self.mouse.up(event, consumed)):
                        if (self.placeholder):
                            pymunkObject = None
                            if (self.tool == 'Circle'):
                                pymunkObject = Circle(self.id, self.placeholder, math.dist(self.placeholder, self.mouse.position))
                            elif (self.tool == 'Rectangle'):
                                pymunkObject = Rectangle(self.id, self.placeholder, self.mouse.position)
                            elif (self.tool == 'Square'):
                                pymunkObject = Square(self.id, self.placeholder, self.mouse.position)
                            if (pymunkObject):
                                pymunkObject.place(self.space)
                                self.objects.append(pymunkObject)
                                self.id += 1
                            self.placeholder = None
                            self.commands.record()
                            break

                if (self.tool == 'Move'):
                    for obj in self.objects:
                        offset = obj.clicked(event, consumed)
                        if (offset):
                            self.offset = offset
                            self.selected_object = obj
                            self.mouse.hold = True
                            break
                    if (self.selected_object and self.mouse.dragging(event)):
                        position = (self.mouse.position[0] + self.offset[0], self.mouse.position[1] + self.offset[1])
                        self.selected_object.set_position(position)
                    if (self.mouse.up(event, consumed)):
                        self.selected_object = None
                if (self.tool == 'Spring'):
                    offset = None
                    for obj in self.objects:
                        offset = obj.clicked(event, consumed)
                        if (offset):
                            offset = (-1*offset[0], -1*offset[1])
                            if (not self.current_constraint):
                                self.current_constraint = DampedSpring(obj, offset)
                            else:
                                self.current_constraint.set_body_b(obj, offset)
                                self.constraints.append(self.current_constraint)
                                self.current_constraint.place(self.space)
                                self.commands.record()
                                self.current_constraint = None
                            break

                    if (not offset and self.mouse.down(event, consumed)):
                        if (not self.current_constraint):
                            print('creating damped string')
                            self.current_constraint = DampedSpring(self.space.static_body, self.mouse.position)
                        else:
                            self.current_constraint.set_body_b(self.space.static_body, self.mouse.position)
                            self.constraints.append(self.current_constraint)
                            self.current_constraint.place(self.space)
                            self.commands.record()
                            self.current_constraint = None
            
            self.draw()
            self.clock.tick(60)
            if (not self.paused):
                self.space.step(1/60)
    
    def draw(self):
        self.window.fill((255, 255, 255))

        for border in self.borders:
            pg.draw.polygon(self.window, (0, 0, 0), border)

        for button in self.buttons.values():
            button.draw(self.window)

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
            self.simulation.paused = True
        else:
            self.simulation.paused = False
        
        self.simulation.playing = not self.simulation.playing
        self.simulation.tool = None
    
    def pause(self):
        self.simulation.paused = not self.simulation.paused
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
        for jsonObject in jsonObjects:
            pymunkObject = None
            if jsonObject.get('type') == 'Circle':
                pymunkObject = Circle.from_json(jsonObject)
            elif jsonObject.get('type') == 'Rectangle':
                pymunkObject = Rectangle.from_json(jsonObject)
            elif jsonObject.get('type') == 'Square':
                pymunkObject = Square.from_json(jsonObject)
            if (pymunkObject):
                pymunkObject.place(self.simulation.space)
                returnedData['objects'].append(pymunkObject)
        for jsonConstraint in jsonConstraints:
            pymunkConstraint = None
            if jsonConstraint.get('type') == 'DampedSpring':
                pymunkConstraint = DampedSpring.from_json(jsonConstraint, self.simulation.space, returnedData['objects'])
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
        self.simulation.paused = True
        self.simulation.tool = None


if __name__ == '__main__':
    simulation = Simulation()

