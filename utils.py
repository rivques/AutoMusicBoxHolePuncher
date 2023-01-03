def enum(*sequential, **named): # https://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    enums = dict(zip(sequential, sequential), **named)
    enums["keys"] = enums.keys()
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

HolePuncherState = enum("OFF", "STARTUP", "IDLE", "PUNCHING")

class Operation:
    pass