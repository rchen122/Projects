from turtle import Turtle


class Score(Turtle):

    def __init__(self):
        super().__init__()
        self.score = 0
        self.high_score = 0
        self.open_high_score()
        self.color("white")
        self.penup()
        self.goto(0, 270)
        self.hideturtle()
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        self.write(f"Score: {self.score} High Score: {self.high_score}", False, "center", ("Courier", 24, "normal"))

    def increment(self):
        self.score += 1
        self.update_scoreboard()

    def reset(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        self.score = 0
        self.update_scoreboard()

    def open_high_score(self):
        with open("highscore.txt") as file:
            self.high_score = int(file.read())

    def save_high_score(self):
        with open("highscore.txt", mode="w") as file:
            file.write(f"{self.high_score}")
