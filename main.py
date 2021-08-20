import sys
import pygame
import Events
import Game
import Programmer
import os

size = width, height = 1200, 700
fill_colour = 245, 245, 245
board_size = Game.board_size
mouse_down_last_frame = False

# state dict will work as a sort of enum
state_dict = {
    "playing": 0,
    "start": 1,
    "won": 2
}
state = state_dict["start"]

pygame.init()
window = pygame.display.set_mode(size)

# loading and preparing the visual game pieces
square = pygame.image.load('square.png')
robot = pygame.image.load('robot.png')
flag = pygame.image.load('flag.png')
button_outline = pygame.image.load('ButtonOutline.png')
robot = pygame.transform.rotate(robot, -180)
robot_default = robot
robot_pos = 0, 0
flag_pos = 8 * 70, 8 * 70

pygame.font.init()
text = pygame.font.SysFont('Cantarell', 20)
number_renderer = pygame.font.SysFont('Cantarell', 70)
large_text_renderer = pygame.font.SysFont('Cantarell', 120)

executing_instructions = True
stack_as_str = 'Stack . '
instructions_as_str = 'Instructions.'

board_state = {}


# updating the game state will be done through events
def rotate_clockwise(data):
    global robot
    robot = pygame.transform.rotate(robot, -90)


def rotate_counter_clockwise(data):
    global robot
    robot = pygame.transform.rotate(robot, 90)


def update_pos(new_pos: (int, int)):
    global robot_pos
    robot_pos = new_pos


def finish_executing(data):
    global executing_instructions
    executing_instructions = False
    try:
        Events.publish('reset', None)
    except Events.EventNotRegisteredException:
        print('reset event might be misspelled')


def win_game(data):
    global state
    state = state_dict["won"]


def push_as_str(number_to_push: int):
    global stack_as_str
    stack_as_str += str(number_to_push) + '.'


def pop_as_str(data):
    global stack_as_str

    # check if the stack is empty
    if stack_as_str == 'Instructions.':
        return

    stack_as_str = stack_as_str[:-2]


def load_board(board_dict):
    global board_state
    board_state = board_dict


def execute(data):
    global executing_instructions
    executing_instructions = True


def update_visuals(data):
    global fill_colour
    global executing_instructions
    global robot_pos

    window.fill(fill_colour)

    # draw the grid
    for vert in range(board_size):
        for horiz in range(board_size):
            coord = (horiz * 70, vert * 70)
            window.blit(square, coord)
            horiz += 1
        vert += 1

    # drawing the numbers on the board
    for value in board_state:
        number = number_renderer.render(str(value["value"]), False, (0, 255, 0))
        pos = value["xPos"] * 70, value["yPos"] * 70
        window.blit(number, pos)

    draw_list(instructions_as_str, 720, 10)

    if executing_instructions:
        draw_list(stack_as_str, 850, 10)

    # if we're not executing we'll display the programmer interface
    else:
        for each_button in buttons:
            each_button.draw()

    # drawing the end flag
    window.blit(flag, flag_pos)

    window.blit(robot, robot_pos)

    # display text boxes if needed
    if state == state_dict["won"]:
        draw_text_box(300, 700, 'You win!')

    elif state == state_dict["start"]:
        draw_text_box(300, 700, 'Click to start')

    pygame.display.flip()


def reset(data):
    global stack_as_str
    global instructions_as_str
    global executing_instructions

    stack_as_str = 'Stack.'
    instructions_as_str = 'Instructions.'
    executing_instructions = False


def add_instruction(instruction):
    global instructions_as_str
    instructions_as_str += str(instruction) + '.'


def reset_robot_visual(data):
    global robot
    global robot_default

    robot = robot_default


Events.subscribe('turn_clockwise', rotate_clockwise)
Events.subscribe('turn_counter_clockwise', rotate_counter_clockwise)
Events.subscribe('update_pos', update_pos)
Events.subscribe('out_of_instructions', finish_executing)
Events.subscribe('game_win', win_game)
Events.subscribe('stack_push', push_as_str)
Events.subscribe('stack_pop', pop_as_str)
Events.subscribe('load_board', load_board)
Events.subscribe('execute', execute)
Events.subscribe('update_visuals', update_visuals)
Events.subscribe('reset', reset)
Events.subscribe('add_byte', add_instruction)
Events.subscribe('reset', reset_robot_visual)


# class for GUI buttons
class Button:
    def __init__(self, x_pos: int, y_pos: int, button_text: str, event_type: str, event_data):
        self.button_x = x_pos
        self.button_y = y_pos
        self.pos = x_pos, y_pos
        self.button_str = button_text
        self.event = event_type
        self.data = event_data
        self.button_text = text.render(button_text, False, (0, 0, 255))

    def mouse_was_pressed(self):
        (mouse_x, mouse_y) = pygame.mouse.get_pos()
        (size_x, size_y) = button_outline.get_size()

        if self.button_x < mouse_x < self.button_x + size_x and self.button_y < mouse_y < self.button_y + size_y:
            try:
                Events.publish(self.event, self.data)
            except Events.EventNotRegisteredException:
                print(f'{self.event} event might be misspelled')

    def draw(self):
        text_pos = (self.button_x + 10, self.button_y + 3)
        window.blit(button_outline, self.pos)
        window.blit(self.button_text, text_pos)


buttons = [
    Button(850, 10, 'Push', 'add_byte', 0x00),
    Button(850, 50, 'Add', 'add_byte', 0x01),
    Button(850, 90, 'Subtract', 'add_byte', 0x02),
    Button(850, 130, 'Forward', 'add_byte', 0x03),
    Button(850, 170, 'Turn R', 'add_byte', 0x04),
    Button(850, 210, 'Turn L', 'add_byte', 0x05),
    Button(850, 250, 'Run Code', 'execute', None)
]


# this function will take a string, split it at he periods and draw it out vertically
def draw_list(str_list: str, x_pos: int, y_offset: int):
    strings = str_list.split('.')
    horizontal_offset = y_offset

    for string in strings:
        surface = text.render(string, False, (0, 0, 255))
        window.blit(surface, (x_pos, horizontal_offset))
        horizontal_offset += 25


# this will draw a centered text box on screen
def draw_text_box(rect_height: int, rect_width: int, x_text: str):
    rect_corner_x = (width - rect_width) / 2
    rect_corner_y = (height - rect_height) / 2
    rect = pygame.Rect(rect_corner_x, rect_corner_y, rect_width, rect_height)
    pygame.draw.rect(window, (0, 0, 0), rect)

    text_surface = large_text_renderer.render(x_text, False, (0, 255, 0))
    text_width, text_height = text_surface.get_size()
    text_corner_x = (width - text_width) / 2
    text_corner_y = (height - text_height) / 2
    window.blit(text_surface, (text_corner_x, text_corner_y))


def process_mouse():
    global state

    # ignores inputs if mouse was pressed on the previous frame
    global mouse_down_last_frame
    (but1, but2, but3) = pygame.mouse.get_pressed(num_buttons=3)

    if not mouse_down_last_frame and but1:
        mouse_down_last_frame = True

        # this checks if there's a "click to continue" text bow on screen, or if we're trying to click buttons
        if state != state_dict["playing"]:
            state = state_dict["playing"]

        elif not executing_instructions:
            for each_button in buttons:
                each_button.mouse_was_pressed()

    # Resets mouse_down_last_frame if the mouse is no longer down
    elif mouse_down_last_frame and not but1:
        mouse_down_last_frame = False


# load in the board
path = os.getcwd() + '/TEST.board'
Game.load_board(path)

# gameloop
while True:
    # check if we're trying to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # if we're executing we'll ignore player inputs and display the stack and instruction list
    if executing_instructions:
        try:
            Events.publish('update', None)
        except Events.EventNotRegisteredException:
            print('update event might be misspelled')

    process_mouse()

    # this update is made through an event so we can call it during the robots movements
    try:
        Events.publish('update_visuals', None)
    except Events.EventNotRegisteredException:
        print('update_visuals event might be misspelled')
