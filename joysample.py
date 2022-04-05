import pygame

# os.environ["SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
import os

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

from dataclasses import dataclass

# Define some colors.
BLACK = pygame.Color("black")
WHITE = pygame.Color("white")


print("pg", pygame.version.ver)
print("sdl", pygame.get_sdl_version())

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

# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((500, 700))

pygame.display.set_caption("My Game")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Initialize the joysticks.
pygame.joystick.init()

# Get ready to print.
textPrint = TextPrint()


# -------- Main Program Loop -----------
while not done:

# def main_loop():
    # global done    
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get():  # User did something.
        if event.type == pygame.QUIT:  # If user clicked close.
            done = True  # Flag that we are done so we exit this loop.
        # elif event.type == pygame.JOYBUTTONDOWN:
        #     print("Joystick button pressed.")
        # elif event.type == pygame.JOYBUTTONUP:
        #     print("Joystick button released.")

    #
    # DRAWING STEP
    #
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    textPrint.reset()

    # Get count of joysticks.
    joystick_count = pygame.joystick.get_count()

    textPrint.tprint(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()

    # For each joystick:
    for j in range(joystick_count):
        joystick = pygame.joystick.Joystick(j)
        joystick.init()

        try:
            jid = joystick.get_instance_id()
        except AttributeError:
            # get_instance_id() is an SDL2 method
            jid = joystick.get_id()
        textPrint.tprint(screen, "Joystick[{}]:  {}".format(j,jid))
        textPrint.indent()

        # Get the name from the OS for the controller/joystick.
        name = joystick.get_name()
        textPrint.tprint(screen, "Joystick name: {}".format(name))

        try:
            guid = joystick.get_guid()
        except AttributeError:
            # get_guid() is an SDL2 method
            pass
        else:
            textPrint.tprint(screen, "GUID: {}".format(guid))

        # 

        hat_list = [joystick.get_hat(i) for i in range(joystick.get_numhats())]
        axis_list = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        button_list = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        # axes = joystick.get_numaxes()
        axes = len(axis_list)
        textPrint.tprint(screen, "Number of axes: {}".format(axes))
        textPrint.indent()


        for i in range(axes):
            # axis = joystick.get_axis(i)
            axis = axis_list[i]
            textPrint.tprint(screen, "Axis {} value: {:>6.3f}".format(i, axis))
        textPrint.unindent()

        # buttons = joystick.get_numbuttons()
        buttons = len(button_list)
        textPrint.tprint(screen, "Number of buttons: {}".format(buttons))
        textPrint.indent()

        #
        #
        #

        trigger_thresh = -0.4

        pressed_pause = button_list[7]
        pressed_jump = button_list[0] or button_list[3]
        pressed_dash = button_list[2] or button_list[1]
        pressed_grab = any(
            [button_list[5], axis_list[5] > trigger_thresh, button_list[4], axis_list[4] > trigger_thresh]
        )
        # pressed_grab = bool(pressed_grab)

        pressed_up = hat_list[0][1] == 1
        pressed_down = hat_list[0][1] == -1
        pressed_left = hat_list[0][0] == -1
        pressed_right = hat_list[0][0] == 1

        stick_left_ud = axis_list[1]
        stick_left_lr = axis_list[0]

        textPrint.tprint(screen, f"Jump: {pressed_jump}")
        textPrint.tprint(screen, f"Dash: {pressed_dash}")
        textPrint.tprint(screen, f"Grab: {pressed_grab}")
        textPrint.tprint(screen, f"Up: {pressed_up}")

        #
        #
        for i in range(buttons):
            # button = joystick.get_button(i)
            button = button_list[i]
            textPrint.tprint(screen, "Button {:>2} value: {}".format(i, button))
        textPrint.unindent()

        hats = joystick.get_numhats()
        textPrint.tprint(screen, "Number of hats: {}".format(hats))
        textPrint.indent()

        # Hat position. All or nothing for direction, not a float like
        # get_axis(). Position is a tuple of int values (x, y).

        for i in range(hats):
            # hat = joystick.get_hat(i)
            hat = hat_list[i]
            textPrint.tprint(screen, "Hat {} value: {}".format(i, str(hat)))
        textPrint.unindent()

        textPrint.unindent()

    #
    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    #

    # Go ahead and update the screen with what we've drawn.
    # pygame.display.flip()
    pygame.display.update()

    # Limit to 20 frames per second.
    clock.tick(60)

# Close the window and quit.
# If you forget this line, the program will 'hang'

# while not done:
#     main_loop()
# on exit if running from IDLE.
pygame.quit()
