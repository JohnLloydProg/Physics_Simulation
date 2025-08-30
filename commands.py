import pygame as pg
from main import Simulation
from ui import ToolButton
from tkinter import filedialog
from tkinter import messagebox
import pickle
from constraints.damped_spring import DampedSpring
from constraints.pin_joint import PinJoint
from constraints.gear_joint import GearJoint
from constraints.constraint import PymunkConstraint
from objects.pymunk_object import PymunkObject
from objects.circle import Circle
from objects.rectangle import Rectangle
from objects.square import Square
from typing import Callable


class Tools:
    undoStack = []
    redoStack = []

    def __init__(self, simulation:Simulation):
        self.simulation = simulation
        self.undoStack = [self.encrypt()]
        self.shorcuts = {
            'delete':self.delete,
            'ctrl+z':self.undo,
            'ctrl+y':self.redo,
            'ctrl+s':lambda: self.save(self.simulation.file),
            'ctrl+shift+s':self.save,
            'ctrl+o':self.load,
            'ctrl+[':lambda: self.simulation.selected_object.move_back() if self.simulation.selected_object else None,
            'ctrl+]':lambda: self.simulation.selected_object.move_front() if self.simulation.selected_object else None,
        }
    
    def file_select(self, option:str):
        if ('New' in option):
            if ((self.simulation.objects or self.simulation.constraints)):
                response = messagebox.askyesnocancel('Save', 'Do you want to save your current simulation?')
                if (response):
                    self.save(self.simulation.file)
            self.clear()
            self.simulation.file = ''
            pg.display.set_caption('Physics Simulation')
        elif ('Load' in option):
            if ((self.simulation.objects or self.simulation.constraints)):
                response = messagebox.askyesnocancel('Save', 'Do you want to save your current simulation?')
                if (response):
                    self.save(self.simulation.file)
            self.load()
        elif ('Save As' in option):
            self.save()
        elif ('Save' in option):
            self.save(self.simulation.file)
    
    def edit_select(self, option:str):
        if ('Undo' in option):
            self.undo()
        elif ('Redo' in option):
            self.redo()
        elif ('Delete' in option):
            self.delete()
    
    def delete(self):
        if (self.simulation.selected_object and not self.simulation.tool):
            self.simulation.selected_object.remove(self.simulation.space)
            self.simulation.objects.remove(self.simulation.selected_object)
            for constraint in self.simulation.constraints:
                if  constraint.body_a == self.simulation.selected_object or constraint.body_b == self.simulation.selected_object:
                    constraint.remove(self.simulation.space)
                    self.simulation.constraints.remove(constraint)
            self.simulation.selected_object = None
            self.record()
        elif (self.simulation.selected_constraint and not self.simulation.tool):
            self.simulation.selected_constraint.remove(self.simulation.space)
            self.simulation.constraints.remove(self.simulation.selected_constraint)
            self.simulation.selected_constraint = None
            self.record()
    
    def changeTool(self, tool):
        if (tool != self.simulation.tool):
            self.simulation.tool = tool
        else:
            self.simulation.tool = None
        print(self.simulation.tool)
    
    def start(self):
        self.simulation.playing = not self.simulation.playing

        if (not self.simulation.playing):
            for object in self.simulation.objects:
                object.reset()
                self.simulation.space.reindex_shapes_for_body(object.body)
        
        for key, button in self.simulation.buttons.items():
            if (key != 'start' and key != 'pause'):
                button.clickable = not self.simulation.playing
        
        
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
        
        data = self.decrypt(read_data)
        self.simulation.objects = data['objects']
        self.simulation.constraints = data['constraints']
        pg.display.set_caption(asked_file)

    def save(self, file:str=''):
        asked_file = filedialog.asksaveasfilename(filetypes=[('Physics Files', '*.phys')]) if not file else file
        if (not asked_file):
            return
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
    
    def decrypt(self, data) -> dict:
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
    
    def collide(self):
        for obj in self.simulation.group_select:
            obj.group_id = self.simulation.group
            obj.shape.group_id = self.simulation.group
            self.simulation.group += 1
