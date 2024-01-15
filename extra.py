from pyscript import display

def dump(obj):
    display(repr(obj))
    for attr in dir(obj):
        if attr.startswith("v"):
            display(attr + " = " + repr(getattr(obj, attr)))
