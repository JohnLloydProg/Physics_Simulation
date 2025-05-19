import pymunk as pm
import pygame as pg
pg.init()
from objects.pymunk_object import PymunkObject
from objects.circle import Circle
from objects.rectangle import Rectangle
from objects.square import Square
from ui import ToolButton, TextButton
from mouse import Mouse
import math
import pickle


class Simulation:
    running = True
    objects:list = []
    tool = None
    placeholder = None
    playing = False
    paused = False

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
            'start':TextButton(10, 820, 340, 70, self.commands.start, (255, 255, 0), 'Start'), 
            'pause':TextButton(10, 740, 340, 70, self.commands.pause, (255, 0, 255), 'Pause'),
            'clear':TextButton(10, 660, 340, 70, self.commands.clear, (0, 255, 255), 'Clear')
        }
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
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    pg.quit()
                    quit()
                
                self.mouse.move(event)
                if (self.tool in ['Circle', 'Rectangle', 'Square']):
                    if (self.mouse.down(event)):
                        if (1430 >= self.mouse.position[0] >= 370 and 890 >= self.mouse.position[1] >= 10):
                            self.placeholder = self.mouse.position
                    if (self.mouse.up(event)):
                        if (self.placeholder):
                            self.commands.record()
                            if (self.tool == 'Circle'):
                                circle = Circle(self.placeholder, math.dist(self.placeholder, self.mouse.position))
                                self.objects.append(circle)
                            elif (self.tool == 'Rectangle'):
                                rectangle = Rectangle(self.placeholder, self.mouse.position)
                                self.objects.append(rectangle)
                            elif (self.tool == 'Square'):
                                square = Square(self.placeholder, self.mouse.position)
                                self.objects.append(square)
                            self.placeholder = None
                
                for button in self.buttons.values():
                    button.clicked(event)
                
                for object in self.objects:
                    object.clicked(event)
            
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
        pg.display.update()


class Tools:
    undoStack = []
    redoStack = []

    def __init__(self, simulation:Simulation):
        self.simulation = simulation
    
    def changeTool(self, tool):
        if (tool != self.simulation.tool):
            self.simulation.tool = tool
        else:
            self.simulation.tool = None
        print(self.simulation.tool)
    
    def start(self):
        for object in self.simulation.objects:
            if (not self.simulation.playing):
                object.place(self.simulation.space)
            else:
                object.remove(self.simulation.space)
                    
        self.simulation.playing = not self.simulation.playing
        self.simulation.paused = False
    
    def pause(self):
        self.simulation.paused = not self.simulation.paused
    
    def load(self):
        pass

    def save(self):
        pass

    def undo(self):
        if (self.undoStack):
            action = self.undoStack.pop()
            self.redoStack.append(self.encrypt())
            self.simulation.objects.clear()
            self.simulation.objects = self.decrypt(action)
            print(self.simulation.objects)
            print(self.undoStack)
    
    def redo(self):
        if (self.redoStack):
            action = self.redoStack.pop()
            self.undoStack.append(self.encrypt())
            self.simulation.objects.clear()
            self.simulation.objects = self.decrypt(action)
    
    def record(self):
        self.undoStack.append(self.encrypt())
        self.redoStack.clear()

    def encrypt(self):
        data = [pymunkObject.json() for pymunkObject in self.simulation.objects]
        self.saved = pickle.dumps(data)
        return pickle.dumps(data)
    
    def decrypt(self, data):
        jsonObjects = pickle.loads(data)
        data = []
        for jsonObject in jsonObjects:
            if jsonObject.get('type') == 'Circle':
                data.append(Circle.from_json(jsonObject))
            elif jsonObject.get('type') == 'Rectangle':
                data.append(Rectangle.from_json(jsonObject))
            elif jsonObject.get('type') == 'Square':
                data.append(Square.from_json(jsonObject))
        return data

    def clear(self):
        if (self.simulation.playing):
            self.start()
        self.simulation.objects.clear()


if __name__ == '__main__':
    simulation = Simulation()

