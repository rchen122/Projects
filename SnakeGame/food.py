from turtle import Turtle
import random
X_POS = Y_POS = [-260, -240, -220, -200, -180, -160, -140, -120, -100, -80, -60, -40, -20, 20, 40, 60, 80, 100, 120,
                140, 160, 180, 200, 220, 240, 260]


class Food(Turtle):

    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.penup()
        self.shapesize(stretch_len=0.5, stretch_wid=0.5)
        self.color("blue")
        self.speed("fastest")
        self.refresh()

    def refresh(self):
        random_x = random.choice(X_POS)
        random_y = random.choice(Y_POS)
        self.goto(random_x, random_y)
