"""A colorful turtle graphics demo.

Draws a multi-pattern scene: a rainbow spiral, a star,
and a row of flowers. Close the window to exit.
"""

import turtle
import colorsys

screen = turtle.Screen()
screen.title("Turtle Graphics Demo")
screen.bgcolor("black")
screen.speed(0)

# --- Pattern 1: Rainbow spiral ---
spiral = turtle.Turtle()
spiral.speed(0)
spiral.hideturtle()
spiral.width(2)

for i in range(200):
    # Cycle through rainbow colors using HSV
    hue = i / 200.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    spiral.pencolor(r, g, b)
    spiral.forward(i)          # each step grows longer
    spiral.left(92)            # slight twist -> spiral effect

# Move to a new spot for the star
spiral.penup()
spiral.goto(-200, -150)
spiral.pendown()

# --- Pattern 2: Five-pointed star ---
star = spiral
star.pencolor("gold")
star.width(3)
for _ in range(5):
    star.forward(150)
    star.right(144)            # 144-degree turn makes a 5-point star

# --- Pattern 3: Row of simple flowers ---
flower = turtle.Turtle()
flower.speed(0)
flower.hideturtle()
flower.width(2)

def draw_flower(t, x, y, petal_color, center_color):
    """Draw a simple flower with 6 petals at (x, y)."""
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.pencolor(petal_color)
    for _ in range(6):
        t.circle(30, 60)      # draw one petal arc
        t.left(60)            # rotate for the next petal
    # Center dot
    t.penup()
    t.goto(x, y - 12)
    t.pendown()
    t.dot(24, center_color)

colors = ["violet", "cyan", "magenta", "orange", "springgreen"]
x_start = -220
for i, color in enumerate(colors):
    draw_flower(flower, x_start + i * 110, -180, color, "yellow")

screen.mainloop()
