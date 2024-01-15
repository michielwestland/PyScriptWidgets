from pyscript import display

def dump(obj):
    display(repr(obj))
    for attr in dir(obj):
        if not attr.startswith("__"):
            display(attr + " = " + repr(getattr(obj, attr)))
