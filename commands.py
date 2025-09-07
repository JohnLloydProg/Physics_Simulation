import pygame as pg
from tkinter import filedialog
from tkinter import messagebox
from main import Simulation
import pickle
from constraints.damped_spring import DampedSpring
from constraints.pin_joint import PinJoint
from constraints.gear_joint import GearJoint
from constraints.pivot_joint import PivotJoint
from constraints.square_joint import SquareJoint
from constraints.constraint import PymunkConstraint
from objects.pymunk_object import PymunkObject
from objects.circle import Circle
from objects.rectangle import Rectangle
from objects.square import Square
from objects.pin import Pin


class Tool:
    def __init__(self, simulation:Simulation, shortcut_key:str=''):
        self.shortcut_key = shortcut_key
        self.simulation = simulation
    
    def call(self):
        pass

    def shortcut(self, event:pg.event.Event, ctrl:bool, shift:bool) -> None:
        if ('ctrl' in self.shortcut_key and ctrl):
            if ('shift' in self.shortcut_key and not shift):
                return
            if (pg.key.name(event.key) in self.shortcut_key):
                self.call()


class Delete(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation)
    
    def shortcut(self, event, ctrl, shift):
        if (event.key == pg.K_DELETE and not ctrl and not shift):
            self.call()
    
    def call(self):
        if (self.simulation.selected_object and not self.simulation.tool):
            self.simulation.selected_object.remove(self.simulation.space)
            self.simulation.objects.remove(self.simulation.selected_object)
            for constraint in self.simulation.constraints:
                if  constraint.body_a == self.simulation.selected_object or constraint.body_b == self.simulation.selected_object:
                    constraint.remove(self.simulation.space)
                    self.simulation.constraints.remove(constraint)
            self.simulation.selected_object = None
            self.simulation.commands['record'].call()
        elif (self.simulation.selected_constraint and not self.simulation.tool):
            print('deleting constraint')
            self.simulation.selected_constraint.remove(self.simulation.space)
            self.simulation.constraints.remove(self.simulation.selected_constraint)
            self.simulation.selected_constraint = None
            self.simulation.commands['record'].call()


class New(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation, 'ctrl+n')
    
    def call(self):
        if ((self.simulation.objects or self.simulation.constraints)):
            response = messagebox.askyesnocancel('Save', 'Do you want to save your current simulation?')
            if (response):
                    self.simulation.commands['save'].call()
            self.simulation.commands['clear'].call()
            self.simulation.undoStack = [self.simulation.commands['encrypt'].call()]
            self.simulation.file = ''
            pg.display.set_caption('Physics Simulation')


class Load(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation, 'ctrl+o')
    
    def call(self):
        if ((self.simulation.objects or self.simulation.constraints)):
            response = messagebox.askyesnocancel('Save', 'Do you want to save your current simulation?')
            if (response):
                self.simulation.commands['save'].call(self.simulation.file)

        try:
            asked_file = filedialog.askopenfilename(filetypes=[('Physics Files', '*.phys')])
            with open(asked_file, 'rb') as f:
                read_data = f.read()
            self.simulation.file = asked_file
            pg.display.set_caption(asked_file)
        except FileNotFoundError as e:
            print(e)
            return
        
        data = self.simulation.commands['decrypt'].call(read_data)
        self.simulation.objects = data['objects']
        self.simulation.constraints = data['constraints']
        self.simulation.undoStack = [self.simulation.commands['encrypt'].call()]
        pg.display.set_caption(asked_file)


class Save(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation, 'ctrl+s')
    
    def call(self):
        asked_file = filedialog.asksaveasfilename(filetypes=[('Physics Files', '*.phys')]) if not self.simulation.file else self.simulation.file
        if (not asked_file):
            return
        file_names = asked_file.split('.')
        if (len(file_names) > 1):
            asked_file = file_names.pop(0)
        data = self.simulation.commands['encrypt'].call()
        
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


class SaveAs(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation, 'ctrl+shift+s')
    
    def call(self):
        self.simulation.file = ''
        self.simulation.commands['save'].call()


class ChangeTool(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation)
    
    def call(self, tool:str):
        if (tool != self.simulation.tool):
            self.simulation.tool = tool
        else:
            self.simulation.tool = None
        print(self.simulation.tool)


class Undo(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation, 'ctrl+z')
    
    def call(self):
        if (len(self.simulation.undoStack) > 1):
            action = self.simulation.undoStack.pop()
            self.simulation.redoStack.append(action)
            self.simulation.commands['clear'].call()
            data = self.simulation.commands['decrypt'].call(self.simulation.undoStack[-1])
            self.simulation.objects = data.get('objects', [])
            self.simulation.constraints = data.get('constraints', [])
            self.simulation.pins = data.get('pins', [])
        self.simulation.tool = None


class Redo(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation, 'ctrl+y')
    
    def call(self):
        if (self.simulation.redoStack):
            action = self.simulation.redoStack.pop()
            self.simulation.undoStack.append(action)
            self.simulation.commands['clear'].call()
            data = self.simulation.commands['decrypt'].call(self.simulation.undoStack[-1])
            self.simulation.objects = data.get('objects', [])
            self.simulation.constraints = data.get('constraints', [])
            self.simulation.pins = data.get('pins', [])
        self.simulation.tool = None


class Start(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation, 'space')
    
    def call(self):
        self.simulation.playing = not self.simulation.playing

        if (not self.simulation.playing):
            for object in self.simulation.objects:
                object.reset()
                self.simulation.space.reindex_shapes_for_body(object.body)
        
        for key, button in self.simulation.buttons.items():
            if (key != 'start' and key != 'pause'):
                button.clickable = not self.simulation.playing
        
        
        self.simulation.tool = None

class Pause(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation)
    
    def call(self):
        self.simulation.playing = not self.simulation.playing
        self.simulation.tool = None


class Record(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation)
    
    def call(self):
        self.simulation.undoStack.append(self.simulation.commands['encrypt'].call())
        self.simulation.redoStack.clear()


class Encrypt(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation)
    
    def call(self):
        data = {'objects':[], 'constraints':[], 'pins':[pin.json() for pin in self.simulation.pins]}
        for pymunkObject in self.simulation.objects:
            data['objects'].append(pymunkObject.json())
        for pymunkConstraint in self.simulation.constraints:
            data['constraints'].append(pymunkConstraint.json())
        return pickle.dumps(data)


class Decrypt(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation)
    
    def call(self, data):
        data = pickle.loads(data)
        jsonObjects = data.get('objects', [])
        jsonConstraints = data.get('constraints', [])
        returnedData = {'objects':[], 'constraints':[]}
        pymunk_objects:dict[str, PymunkObject] = {'Circle':Circle, 'Rectangle':Rectangle, 'Square':Square}
        pymunk_constraints:dict[str, PymunkConstraint] = {'DampedSpring':DampedSpring, 'PinJoint':PinJoint, 'PivotJoint':PivotJoint, 'SquareJoint':SquareJoint, 'GearJoint':GearJoint}
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
        returnedData['pins'] = [Pin.from_json(pin, self.simulation.space, returnedData['objects']) for pin in data.get('pins', [])]
        return returnedData


class Clear(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation)
    
    def call(self):
        for constraint in self.simulation.constraints:
            constraint.remove(self.simulation.space)

        for object in self.simulation.objects:
            object.remove(self.simulation.space)

        self.simulation.objects.clear()
        self.simulation.constraints.clear()
        self.simulation.pins.clear()
        self.simulation.playing = False
        self.simulation.tool = None


class NotCollide(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation)
    
    def call(self):
        print('not colliding')
        for obj in self.simulation.group_select:
            obj.group_id = self.simulation.group
            obj.shape.group_id = self.simulation.group
        self.simulation.group += 1


class Collide(Tool):
    def __init__(self, simulation:Simulation):
        super().__init__(simulation)
    
    def call(self):
        print('colliding')
        for obj in self.simulation.group_select:
            obj.group_id = self.simulation.group
            obj.shape.group_id = self.simulation.group
            self.simulation.group += 1
