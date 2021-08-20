import Events

byte_list = []


# we're gonna interact with the programmer entirely through events
def add_byte(byte):
    global byte_list
    byte_list.append(byte)


def send_code(data):
    global byte_list

    try:
        Events.publish('set_instructions', byte_list)
    except Events.EventNotRegisteredException:
        print('set_instructions event might be misspelled')

    byte_list = []


Events.subscribe('add_byte', add_byte)
Events.subscribe('execute', send_code)
