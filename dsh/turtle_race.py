"""Turtle Racing Game 🏁

A fun turtle race! Pick your turtle, watch them sprint to the
finish line, and see who wins. Press SPACE or click to race again.
"""

import turtle
import random

# --- Game setup ---
screen = turtle.Screen()
screen.title("Turtle Racing Game 🏁")
screen.setup(width=800, height=500)
screen.bgcolor("forestgreen")
screen.tracer(0)              # turn off animation for instant drawing

# --- Racers ---
COLORS = ["red", "blue", "yellow", "purple", "orange", "pink"]
LANE_HEIGHT = 60
START_X = -300
FINISH_X = 280

turtles = []
for i, color in enumerate(COLORS):
    t = turtle.Turtle(shape="turtle")
    t.color(color)
    t.penup()
    t.speed(0)
    # Each turtle gets its own lane, stacked vertically
    y = (i - len(COLORS) / 2 + 0.5) * LANE_HEIGHT
    t.goto(START_X, y)
    t.pendown()               # draw a trail as they race
    t.pensize(3)
    t.left(360)               # face right (turtles default to right)
    turtles.append(t)

# --- Track decorations ---
def draw_track():
    """Draw finish line, lane markers, and start banner."""
    artist = turtle.Turtle()
    artist.hideturtle()
    artist.penup()
    artist.speed(0)

    # Finish line (checkered pattern)
    for y in range(-180, 200, 20):
        artist.goto(FINISH_X, y)
        artist.pendown()
        artist.forward(0)
        artist.dot(12, "black" if (y // 20) % 2 else "white")
    artist.penup()

    # Vertical finish banner
    artist.goto(FINISH_X + 20, 200)
    artist.color("white")
    artist.write("FINISH", font=("Arial", 14, "bold"))

    # Lane numbers
    for i in range(len(COLORS)):
        y = (i - len(COLORS) / 2 + 0.5) * LANE_HEIGHT
        artist.goto(START_X - 40, y - 8)
        artist.write(str(i + 1), font=("Arial", 12, "bold"))

    # Title banner
    artist.goto(0, 210)
    artist.write("🏁 TURTLE RACE 🏁", align="center",
                 font=("Arial", 20, "bold"))

draw_track()
screen.update()

# --- Scoreboard ---
scores = {color: 0 for color in COLORS}

def show_scores():
    board.clear()
    text = "Wins:  " + "   ".join(
        f"{c}:{scores[c]}" for c in COLORS)
    board.goto(0, -225)
    board.write(text, align="center", font=("Arial", 11, "normal"))

board = turtle.Turtle()
board.hideturtle()
board.penup()

# --- Race logic ---
def countdown(n):
    """Show a big 3-2-1 countdown before the race."""
    counter = turtle.Turtle()
    counter.hideturtle()
    counter.penup()
    for i in range(n, 0, -1):
        counter.clear()
        counter.goto(0, 0)
        counter.color("white")
        counter.write(str(i), align="center",
                       font=("Arial", 48, "bold"))
        screen.update()
        turtle.delay(600)     # wait 0.6s per number
        turtle.delay(0)
    counter.clear()
    counter.write("GO!", align="center", font=("Arial", 48, "bold"))
    screen.update()
    counter.clear()

def race():
    """Run one full race; returns the winning turtle's color."""
    # Reset positions
    for t in turtles:
        t.penup()
        t.goto(START_X, t.ycor())
        t.clear()              # erase old trails
        t.pendown()
        t.setheading(0)
    screen.update()

    countdown(3)

    # Race until a turtle crosses the finish line
    while True:
        for t in turtles:
            # Random forward hop with occasional backward stumble
            step = random.randint(2, 12)
            if random.random() < 0.10:        # 10% chance to wobble back
                step = -step // 2
            t.forward(step)

            # Winner check
            if t.xcor() >= FINISH_X:
                t.penup()
                t.goto(FINISH_X, t.ycor())
                return t.pencolor()
        screen.update()

# --- Winner announcement ---
def announce(color):
    """Display winner banner and update the scoreboard."""
    scores[color] += 1
    show_scores()

    banner = turtle.Turtle()
    banner.hideturtle()
    banner.penup()

    # Winner circle
    winner = turtles[COLORS.index(color)]
    winner.turtlesize(2)       # grow the champion!

    banner.goto(0, 100)
    banner.color(color)
    banner.write(f"🏆 {color.upper()} TURTLE WINS! 🏆",
                 align="center", font=("Arial", 24, "bold"))
    banner.goto(0, 70)
    banner.color("white")
    banner.write("Click anywhere (or press SPACE) to race again",
                 align="center", font=("Arial", 12, "italic"))
    screen.update()
    return winner, banner

def reset_race():
    """Clean up winner banner and race again."""
    global current_winner
    if current_winner is not None:
        current_winner.turtlesize(1)   # shrink back to normal
    current_winner = None

# --- Main loop ---
current_winner = None
show_scores()

race_num = 0
MAX_RACES = 5          # run 5 races, then offer exit

while race_num < MAX_RACES:
    winner_color = race()
    current_winner, banner = announce(winner_color)

    # Wait for click or keypress to continue
    continue_flag = []
    screen.onclick(lambda x, y: continue_flag.append(True))
    screen.onkey(lambda: continue_flag.append(True), "space")
    screen.listen()
    turtle.delay(10)
    while not continue_flag:
        screen.update()
    turtle.delay(0)

    # Cleanup for next race
    banner.clear()
    reset_race()
    race_num += 1

# Goodbye message
bye = turtle.Turtle()
bye.hideturtle()
bye.penup()
bye.goto(0, 0)
bye.color("white")
bye.write("Thanks for playing! 🐢 Final scoreboard above.",
          align="center", font=("Arial", 16, "bold"))
screen.update()

screen.mainloop()
