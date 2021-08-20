event_dict = {}


def subscribe(event_type: str, func):
    if event_type not in event_dict:
        event_dict[event_type] = []
        # print(f'created event {event_type}')
    event_dict[event_type].append(func)
    # print(f'{func.__name__} has subscribed to {event_type}')


# if there is no data to publish, the data will be None, and the subscriber will have "data" as their only argument
def publish(event_type: str, data):
    if event_type not in event_dict:
        raise EventNotRegisteredException

    for func in event_dict[event_type]:
        func(data)


class EventNotRegisteredException(Exception):
    """Event isn't in the event_dict"""
