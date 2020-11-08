import turtle
import random



#open the turtle screen
s = turtle.getscreen()

# use throughout the program to refer to the turtle
t = turtle.Turtle()

# COLOR
turtle.bgcolor("cyan")
turtle.title("Marving")

# PEN SIZE
t.pensize(5)
# PEN COLOR
t.pencolor("purple")
# COLOR OF TURTLE 
t.fillcolor("red")

def square(self, side):
    self.fd(side)
    self.rt(90)
    self.fd(side)
    self.rt(90)
    self.fd(side)
    self.rt(90)
    self.fd(side)

def circle(self, radius):
    self.circle(radius)

def dot(self, diameter):
    self.dot(diameter)

square(t, 100)
circle(t, 60)
t.forward(20)
dot(t, 50)
t.forward(80)


# PEN UP 
t.penup()
# PEN DOWN 
t.pendown()
# UNDO
t.undu()
# CLEAR
t.clear() 
# t.reset window
t.reset()
# LEAVE A MARK 
t.stamp()



# FOR IN TURTLE
for i in range(4):
    t.fd(100)
    t.rt(90)
    
# WHILE 
n=10
while n <= 40:
    t.circle(n)
    n = n+10



