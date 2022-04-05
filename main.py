# https://stackoverflow.com/questions/550001/fully-transparent-windows-in-pygame

import pygame
import pygame.gfxdraw

import math
from math import pi, sin, cos, tan, atan, atan2, sqrt
from math import degrees as rad2deg, radians as deg2rad

import numpy as np

from dataclasses import dataclass

import os

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"


# PREVIEW_CHROMA = True
PREVIEW_CHROMA = False

#
pygame.init()
pygame.joystick.init()


#


@dataclass
class GameState:
    up = False
    left = False
    down = False
    right = False

    stick_left_ud = 0.0
    stick_left_lr = 0.0

    pause = False
    jump = False
    dash = False
    grab = False


print(f"{pygame.joystick.get_count()=}")

# def poll_state(joystick_idx: int) -> GameState:
def poll_state(hat_list, axis_list, button_list) -> GameState:
    #
    trigger_thresh = -0.4

    #
    # joystick = pygame.joystick.Joystick(joystick_idx)
    # joystick.init()

    # try:
    #     jid = joystick.get_instance_id()
    # except AttributeError:
    #     # get_instance_id() is an SDL2 method
    #     jid = joystick.get_id()
    # name = joystick.get_name()
    # try:
    #     guid = joystick.get_guid()
    # except AttributeError:
    #     # get_guid() is an SDL2 method
    #         pass

    # print(guid)
    #
    # pygame.event.pump()
    # hat_list = [joystick.get_hat(i) for i in range(joystick.get_numhats())]
    # axis_list = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
    # button_list = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
    # print(button_list)

    # if any(button_list):
    #     print(button_list)
    state = GameState()

    state.up = hat_list[0][1] == 1
    state.down = hat_list[0][1] == -1
    state.left = hat_list[0][0] == -1
    state.right = hat_list[0][0] == 1

    state.stick_left_ud = axis_list[1]
    state.stick_left_lr = axis_list[0]

    state.pause = button_list[7]
    state.jump = button_list[0] or button_list[3]
    state.dash = button_list[2] or button_list[1]
    state.grab = any(
        [
            button_list[5],
            axis_list[5] > trigger_thresh,
            button_list[4],
            axis_list[4] > trigger_thresh,
        ]
    )
    return state


screen = pygame.display.set_mode((800, 600))  # For borderless, use pygame.NOFRAME
null_screen = pygame.Surface(screen.get_size())

done = False
# fuchsia = (255, 0, 128)  # Transparency color
# fuchsia = (255, 0, 255)  # Transparency color
fuchsia = (0, 255, 0)  # Transparency color
dark_red = (139, 0, 0)
some_blue = (0, 111, 100, 0)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

COLORA = (255, 255, 255)
COLORB = (200, 200, 200)
COLORC = (170, 170, 0)

ST_PRESSED = (COLORA, None, COLORC)
ST_OFF = (COLORB, COLORA, None)


# Create layered window
if PREVIEW_CHROMA:
    import win32api
    import win32con
    import win32gui

    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(
        hwnd,
        win32con.GWL_EXSTYLE,
        win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED,
    )
    # Set window transparency color
    win32gui.SetLayeredWindowAttributes(
        hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY
    )

# ------------------------------------------------

FPS = pygame.time.Clock()

font = pygame.font.SysFont("arial", 80)

# ------------------------------------------------
counter = 0


def draw_boxed_txt(txt: str, tl, color, color2=None, color3=None):
    if color2 is None:
        color2 = color
    aa = False
    dim = font.size(txt)
    margin = 6
    r = pygame.Rect(tl[0], tl[1], dim[0] + margin * 2, dim[1])
    line_width = 4
    # rtxt = font.render(txt, aa, color, color3)
    rtxt = font.render(txt, aa, color)
    if color3 is not None:
        pygame.draw.rect(screen, color3, r, width=0)
    screen.blit(rtxt, (tl[0] + margin, tl[1]))
    pygame.draw.rect(screen, color2, r, width=line_width)
    return r


def scaled_sincos(theta, r):
    return (r * cos(theta), r * sin(theta))


def draw_pie(color, center, radius, t0, t1):
    angle_set = np.linspace(t0, t1, 35)
    path = [(0, 0)] + [scaled_sincos(t, radius) for t in angle_set]
    # print(path)
    # path = [(0, 0), scaled_sincos(t0, radius), scaled_sincos(t1, radius)]
    path = [(p[0] + center[0], center[1] - p[1]) for p in path]
    pygame.draw.polygon(screen, color, path)


def patan2(y, x):
    theta = atan2(y, x)
    if theta < 0:
        theta = theta + 2 * pi
    return theta


def intersect_unit_div(point, div0, div1):
    theta = patan2(-point[1], point[0])
    if theta < div0:
        theta = theta + 2 * pi
    return div0 < theta < div1


def draw_state(state: GameState):
    fps_str = f"{math.floor(counter/60)}"

    #
    spacing = 10

    style = lambda pressed: ST_PRESSED if pressed else ST_OFF

    root = pygame.Rect(40, 40, 0, 0)
    pen = root
    pen = draw_boxed_txt("Jump", (pen.right, pen.top), *style(state.jump))
    pen = draw_boxed_txt("Dash", (pen.right + spacing, pen.top), *style(state.dash))
    pen = draw_boxed_txt("Grab", (pen.right + spacing, pen.top), *style(state.grab))

    step = 30
    radius = step * 3 / 2

    path = [
        (step * 0, step * 0),
        (step * 1, step * 0),  # Down
        (step * 1, step * 1),
        (step * 2, step * 1),
        (step * 2, step * 0),
        (step * 3, step * 0),
        (step * 3, -step * 1),
        (step * 2, -step * 1),  # Right
        (step * 2, -step * 2),
        (step * 1, -step * 2),  # Up
        (step * 1, -step * 1),
        (step * 0, -step * 1),  # Left
    ]
    path = [(p[0] + pen.right + spacing, p[1] + pen.top + step * 2) for p in path]

    p_l = path[-1]
    p_u = path[-3]
    p_r = path[-5]
    p_d = path[1]

    pad_box = pygame.draw.polygon(null_screen, COLORA, path, width=5)
    # pygame.draw.rect(screen, dark_red, pad_box)

    def fillp(p):
        pygame.draw.rect(screen, COLORC, pygame.Rect(p[0], p[1], step, step))
        # pygame.draw.line(screen, COLORB, pad_box.center, (p[0] + step/2,p[1]+step/2),width=3)
        pygame.draw.line(
            screen,
            COLORB,
            (pen.right + spacing + radius, pen.top + radius),
            (p[0] + step / 2, p[1] + step / 2),
            width=3,
        )

    if state.left:
        fillp(p_l)
    if state.up:
        fillp(p_u)
    if state.right:
        fillp(p_r)
    if state.down:
        fillp(p_d)

    pen = pygame.draw.polygon(screen, COLORA, path, width=5)

    center = (pen.right + spacing + radius, pen.top + radius)

    off_center = lambda p: (center[0] + p[0] * radius, center[1] + p[1] * radius)

    stick = (state.stick_left_lr, state.stick_left_ud)
    stick_pos = off_center(stick)

    unit_val = math.sqrt(3) / 2

    draw_unit = lambda p: pygame.draw.line(screen, BLACK, center, p, width=4)

    # draw_unit(off_center((unit_val, 0.5)))
    # draw_unit(off_center((unit_val, -0.5)))
    # draw_unit(off_center((-unit_val, -0.5)))
    # draw_unit(off_center((-unit_val, 0.5)))

    # draw_unit(off_center((0.5, unit_val)))
    # draw_unit(off_center((0.5, -unit_val)))
    # draw_unit(off_center((-0.5, -unit_val)))
    # draw_unit(off_center((-0.5, unit_val)))

    div_p = [
        (unit_val, -0.5),
        (0.5, -unit_val),
        (-0.5, -unit_val),
        (-unit_val, -0.5),
        (-unit_val, 0.5),
        (-0.5, unit_val),
        (0.5, unit_val),
        (unit_val, 0.5),
    ]
    # div_t = [atan2(p[1], p[0]) for p in div_p]
    div_t = [pi * i / 6 for i in range(12)]
    div_t = [div_t[i] for i in [1, 2, 4, 5, 7, 8, 10, 11]]

    # print(div_t)

    for p in div_p:
        draw_unit(off_center(p))

    if np.linalg.norm(stick) >= 0.5:
        # if True:
        for i in range(len(div_t) - 1):
            arc = div_t[i : i + 2]
            if intersect_unit_div(stick, *arc):
                draw_pie(WHITE, center, radius, *arc)

        arc = [div_t[-1], div_t[0] + 2 * pi]
        if intersect_unit_div(stick, *arc):
            draw_pie(WHITE, center, radius, *arc)
        # draw_pie(WHITE, center, radius, *arc)
        # draw_pie(COLORC, center, radius, 0, pi * 2)
    pygame.draw.line(screen, COLORC, center, stick_pos, width=5)

    pen = pygame.draw.circle(
        screen,
        COLORA,
        center,
        radius + 3,
        width=6,
    )

    input_box = pen
    # pygame.draw.arc(screen,BLACK, input_box,0, math.pi, width=math.ceil(20))

    pygame.draw.circle(screen, COLORB, stick_pos, 10)  # Stick pointer

    # pen = draw_boxed_txt(fps_str, (40, 200), dark_red)
    # pen = draw_boxed_txt("True", (pen.right + spacing, pen.top), *style(True))

    # pen = draw_boxed_txt("----", (pen.right + spacing, pen.top), *ST_PRESSED)
    # pen = draw_boxed_txt(
    #     f"{patan2(-stick[1], stick[0])}", (pen.right + spacing, pen.top), *ST_PRESSED
    # )
    # 
    # END draw state


# def main_loop():
while not done:
    FPS.tick(60)
    # global done
    # global counter

    counter += 1

    # --------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    # pygame.event.pump()

    state = GameState()
    joystick_count = pygame.joystick.get_count()
    if joystick_count >= 1:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        hat_list = [joystick.get_hat(i) for i in range(joystick.get_numhats())]
        axis_list = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        button_list = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
        state = poll_state(hat_list, axis_list, button_list)
        # print(button_list)
        # state = poll_state(1)
    # ------------------

    screen.fill(fuchsia)  # Transparent background
    # ---------

    # pygame.draw.rect(screen, some_blue, pygame.Rect(30, 30, 60, 60), width=0)

    #
    draw_state(state)

    #
    pygame.display.update()
    # FPS.tick(20)

    # END main_loop


# while not done:
#     main_loop()
pygame.quit()
