import json
import Events
from time import sleep

# this is how we're keeping track of the game board
board_values = {}

# basic info misc info
robot_pos_x = 0
robot_pos_y = 0

sleep_time = 0.5

# 0 = N
# 1 = E
# 2 = S
# 3 = W
robot_direction = 2

board_size = 10


# function to reset the robots orientation and position, and
def reset_robot(data):
    global robot_direction
    global robot_pos_x
    global robot_pos_y

    robot_pos_x = 0
    robot_pos_y = 0

    robot_direction = 2

    try:
        Events.publish('update_pos', (0, 0))
    except Events.EventNotRegisteredException:
        print('update_pos event might be misspelled')


Events.subscribe('reset', reset_robot)


# this is how we'll build the game board
def add_board_value(x_pos, y_pos, value):
    pos = x_pos, y_pos
    if pos in board_values:
        raise Exception
    else:
        board_values[pos] = value


# the board will be stored in json files that contains an array of board_value objects called "boards"
# the board_value objects contain the xPos, yPos, and value
def load_board(path: str):
    try:
        file = open(path, 'r')
    except:
        print('file not found')
        return
    board_dict = json.load(file)
    file.close()

    for value in board_dict["boards"]:
        add_board_value(value["xPos"], value["yPos"], value["value"])

    try:
        Events.publish('load_board', board_dict["boards"])
    except Events.EventNotRegisteredException:
        print('load_board event might be misspelled')


# the stack for the interpreter
stack = []


# basic functions for interacting with the stack
def pop():
    if len(stack) == 0:
        return 0
    else:
        try:
            Events.publish('stack_pop', None)
        except Events.EventNotRegisteredException:
            print('stack_pop event might be misspelled')

        return stack.pop()


def push(value):
    try:
        Events.publish('stack_push', value)
    except Events.EventNotRegisteredException:
        print('stack_push event might be misspelled')

    stack.append(value)


# the functions for the interpreter
def walk():
    global robot_direction
    global robot_pos_y
    global robot_pos_x

    i = pop()

    for _ in range(i):
        if robot_direction == 0:
            if robot_pos_y != 0:
                robot_pos_y -= 1
        elif robot_direction == 1:
            if robot_pos_x != board_size - 1:
                robot_pos_x += 1
        elif robot_direction == 2:
            if robot_pos_y != board_size - 1:
                robot_pos_y += 1
        elif robot_direction == 3:
            if robot_pos_x != 0:
                robot_pos_x -= 1

        new_pos = robot_pos_x * 70, robot_pos_y * 70

        try:
            Events.publish('update_pos', new_pos)
        except Events.EventNotRegisteredException:
            print('update_pos event might be misspelled')

        try:
            Events.publish('update_visuals', None)
        except Events.EventNotRegisteredException:
            print('update_visuals event might be misspelled')

        sleep(sleep_time)


def turn_clockwise():
    global robot_direction
    global sleep_time
    i = pop()

    for _ in range(i):
        if robot_direction == 3:
            robot_direction = 0
        else:
            robot_direction += 1

        try:
            Events.publish('turn_clockwise', None)
        except Events.EventNotRegisteredException:
            print('turn_clockwise event might be misspelled')

        try:
            Events.publish('update_visuals', None)
        except Events.EventNotRegisteredException:
            print('update_visuals event might be misspelled')

        sleep(sleep_time)


def turn_counter_clockwise():
    global robot_direction
    global sleep_time
    i = pop()

    for _ in range(i):
        if robot_direction == 0:
            robot_direction = 3
        else:
            robot_direction -= 1

        try:
            Events.publish('turn_counter_clockwise', None)
        except Events.EventNotRegisteredException:
            print('turn_counter_clockwise event might be misspelled')

        try:
            Events.publish('update_visuals', None)
        except Events.EventNotRegisteredException:
            print('update_visuals event might be misspelled')

        sleep(sleep_time)


def push_value():
    pos = robot_pos_x, robot_pos_y
    if pos in board_values:
        push(board_values[pos])
    else:
        print('no value to push')


def add_values():
    a = pop()
    b = pop()
    push(a + b)


def subtract_values():
    a = pop()
    b = pop()
    push(b - a)


# the interpreter is a dict, just to keep it simple
interpreter = {
    0x00: push_value,
    0x01: add_values,
    0x02: subtract_values,
    0x03: walk,
    0x04: turn_clockwise,
    0x05: turn_counter_clockwise}

instructions = []
instruction_count = 0


# this function will set the instructions
def set_instructions(instruction_set: []):
    global instructions
    instructions = instruction_set


def next_instruction(data):
    global instructions
    global instruction_count
    global robot_pos_y
    global robot_pos_x

    # check if there are any more instructions
    if instruction_count == len(instructions):
        try:
            Events.publish('out_of_instructions', None)
        except Events.EventNotRegisteredException:
            print('out_of_instructions event might be misspelled')

        # check if win
        if robot_pos_x == 9 and robot_pos_y == 9:
            try:
                Events.publish('game_win', None)
            except Events.EventNotRegisteredException:
                print('game_win event might be misspelled')

        else:
            try:
                Events.publish('reset', None)
            except Events.EventNotRegisteredException:
                print('reset event might be misspelled')

        instruction_count = 0

    else:
        instruction = instructions[instruction_count]
        interpreter[instruction]()

        instruction_count += 1


Events.subscribe('set_instructions', set_instructions)
Events.subscribe('update', next_instruction)
