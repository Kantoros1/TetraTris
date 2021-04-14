from tkinter import Tk, Canvas, Frame, BOTH
from math import sin, cos, radians
from itertools import product, combinations
from random import choice
from copy import copy, deepcopy

class Tetris(Frame): # Main class
  def __init__(self,master=None):
    super().__init__()

    self.master.title("TetraTris")
    self.pack(fill=BOTH, expand=True)

    self.canvas = Canvas(self,width=1004, height=1004,bg='#ccc')
    self.canvas.configure(scrollregion=(-502, -502, 502, 502))
    self.canvas.pack(fill=BOTH, expand=True)

    self.distribution = [0,0,0,1,1,1,2,2]
    self.template = (
                    [[1,1,1,33],],
                    [[1,1,1,33],[-1,1,1,33]],
                    [[1,1,1,33],[-1,1,1,33],[1,-1,1,33]]
                    )
    self.menuText = ('TetraTris','Play','Difficulty = {}','Help','Exit')
    self.diffText = ('Easy','Medium','Hard')
    self.pointer = 0
    self.difficulty = 0
    self.play = False
    self.over = False
    self.helpMenu = False

    self.bind(master)
    self.menu()

  def menu(self):
    self.canvas.delete('all')
    for index,txt in enumerate(self.menuText):
      color = '#f00' if self.pointer == index-1 else '#000'
      size = 100 if index == 0 else 50
      if index == 2:
        txt = txt.format(self.diffText[self.difficulty])
      self.canvas.create_text(0,-150*(2-index),\
                              fill=color,font=('Courier',size),text=txt)

  def help(self):
    self.canvas.delete('all')
    self.helpMenu = True
    helptext = ('Arrow Keys: Camera','z,x,c,v: Rotate piece','Return: Drop piece','Ok')
    for index,txt in enumerate(helptext):
      color = '#f00' if index == 3 else '#000'
      self.canvas.create_text(0,-150*(2-index),\
                                fill=color,font=('Courier',50),text=txt)

    
  def reset(self):
    self.points3D = []
    self.edges = []
    self.rot = [0,0]
    self.height = 0
    self.shapes = [[],[]]
    self.score = 0
    self.play = True

    self.advance()
    
  def generate(self):
    # Generate the web of points and edges delimiting shapes,
    # so they can be rendered. Called every time shapes change
    self.points3D = []
    self.edges = []

    # Generate points based on cube positions
    for shape in self.shapes:
      points = []
      
      for cube in shape:
        for comb in [*product((-1,1),repeat=4)]:
          
          point = list(map(sum,zip(comb,cube)))
          # Remove uneeded points //TODO: fix edge glitch
          if point in points:
            points.remove(point)
            
          else:
            points.append(point)

      # Add points to point storage
      for point in points:
        if point not in self.points3D:
          self.points3D.append(point)

      # Generate edges (for every shape individualy)
      for point1,point2 in [*combinations(points,r=2)]:
        eq = 0
        
        for val in list(map(lambda val:val[0]-val[1],zip(point1,point2))):
          if val == 0:
            eq += 1
            
        if eq == 3:
          index1 = self.points3D.index(point1)
          index2 = self.points3D.index(point2)
          self.edges.append((index1,index2))

    self.draw()

  def bind(self,master): # Key bindings
    master.bind('<Left>',self.press)
    master.bind('<Right>',self.press)
    master.bind('<Up>',self.press)
    master.bind('<Down>',self.press)
    master.bind('z',self.press)
    master.bind('x',self.press)
    master.bind('c',self.press)
    master.bind('v',self.press)
    master.bind('<Return>',self.press)

  def press(self,event): # Key Registering
    speed = 5
    if   event.keysym == 'Right':
      if self.play == True:
        self.rot[1] -= speed;self.draw()
        
    elif event.keysym == 'Left':
      if self.play == True:
        self.rot[1] += speed;self.draw()
        
    elif event.keysym == 'Up':
      if self.play == True:
        self.rot[0] -= speed;self.draw()
      elif self.pointer > 0:
        self.pointer -= 1
        self.menu()
        
    elif event.keysym == 'Down':
      if self.play == True:
        self.rot[0] += speed;self.draw()
      elif self.pointer < 3:
        self.pointer += 1
        self.menu()
        
    elif event.keysym == 'z': self.rotate((0,1))
    elif event.keysym == 'x': self.rotate((0,2))
    elif event.keysym == 'c': self.rotate((1,2))
    elif event.keysym == 'v': self.rotate((1,3))
    elif event.keysym == 'Return':
      if self.helpMenu == True:
        self.helpMenu = False
        self.menu()
        
      elif self.play == True:
        if self.shapes[1] != []:
          self.fall()

      elif self.over == True:
        self.over = False
        self.menu()
        
      elif self.pointer == 0:
        self.reset()
        
      elif self.pointer == 1:
        self.difficulty += 1
        
        if self.difficulty > 2:
          self.difficulty = 0

        self.menu()

      elif self.pointer == 2:
        self.helpMenu = True
        self.help()

      elif self.pointer == 3:
        self.master.destroy()

  def draw(self): # Draw 2D points on the screen. Called for every frame
    self.canvas.delete('all')
    points2D = []
    for P in self.points3D:
      point = [0,0,0,0]
      for coor in range(3):
        point[coor] += .1 * P[3] * P[coor]
        
      sin_X = sin(radians(self.rot[0]))
      cos_X = cos(radians(self.rot[0]))
      sin_Y = sin(radians(self.rot[1]))
      cos_Y = cos(radians(self.rot[1]))
      
      X = cos_Y*point[0] + sin_Y*point[2]
      Y = sin_X*sin_Y*point[0] + cos_X*point[1] - sin_X*cos_Y*point[2]

      X = int(X * 50)
      Y = int(Y * -50)

      points2D.append((X,Y))

    for V1,V2 in self.edges:
      start = points2D[V1]
      end = points2D[V2]
      
      self.canvas.create_line(*start,*end,width=3)

    self.canvas.create_text(-300,400,fill='#000',font=('Courier',30),\
                            text='Score:{}'.format(self.score))


  def new(self): # New piece
    self.shapes[1] = deepcopy(self.template[choice(self.distribution)])
    self.height = 33
    if self.isColliding():
      self.gameOver()

    else:
      self.generate()

  def isColliding(self): # check for collision of falling shape and base
    for cube in self.shapes[1]:
      future = copy(cube)
      
      future[3] -= 2
      if future[3] == 5:
        return True
      if future in self.shapes[0]:
        return True
    return False

  def combine(self): # Combine the falling shape with the base
    for cube in self.shapes[1]:
      self.shapes[0].append(cube)
      
    self.shapes[1] = []


  def rotate(self,axis): # Rotate falling block
    for index,cube in enumerate(self.shapes[1]):
      axis_1 = cube[axis[0]]
      axis_2 = cube[axis[1]]

      if axis[1] == 3:
        axis_2 -= self.height + 1

      if axis_1 * axis_2 > 0:
        if axis_2 > 0:
          self.shapes[1][index][axis[1]] -= 2
        else:
          self.shapes[1][index][axis[1]] += 2
      else:
        if axis_1 > 0:
          self.shapes[1][index][axis[0]] -= 2
        else:
          self.shapes[1][index][axis[0]] += 2

    self.generate()


  def fall(self): # Make block fall immidiatelly
    while self.isColliding() == False:
      for index,point in enumerate(self.shapes[1]):
        self.shapes[1][index][3] -= 2
      self.height -= 2

    self.combine()
    self.clear()
    self.new()

  def clear(self): # clear full layers

    for layer in range(1,33,2):

      clr = True
      for C in [*product((-1,1),repeat=3)]:
        coor = [*C]
        coor.append(layer)
        if coor not in self.shapes[0]:
          clr = False
          break

      if clr == True:
        self.score += 100
        
        self.shapes[0] = list(filter(lambda coor: coor[3] != layer, self.shapes[0]))

        for index,coor in enumerate(self.shapes[0]):
          if coor[3] > layer:
            self.shapes[0][index][3] -= 2


  def gameOver(self): # Game over screen
    self.canvas.delete('all')
    self.canvas.create_text(0,-100,fill='#000',font=('Courier',100),text='Game Over')
    self.canvas.create_text(0,100,fill='#000',font=('Courier',50),text='Score:{}'.format(self.score))
    self.play = False
    self.over = True

  def advance(self): # Main method
    if self.play == True:
      if self.shapes[1] == []:
        self.new()

      else:
        for index,point in enumerate(self.shapes[1]):
          self.shapes[1][index][3] -= 2
        self.height -= 2

        if self.isColliding():
          self.combine()
          self.clear()
          
        self.generate()
        
      self.after(max(int(500*(3-self.difficulty)-(self.score/100)),50),self.advance)


root = Tk()
app = Tetris(root)
root.geometry('1000x1000+0+0')
root.resizable(False,False)
root.title('TetraTris')
root.mainloop()
