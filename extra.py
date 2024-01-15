from pyscript import display
import pickle
import base64

# See: https://oren-sifri.medium.com/serializing-a-python-object-into-a-plain-text-string-7411b45d099e

# Serialize an object into a plain text
def obj_to_txt(obj):
    message_bytes = pickle.dumps(obj)
    base64_bytes = base64.b64encode(message_bytes)
    txt = base64_bytes.decode('ascii')
    return txt

# De-serialize an object from a plain text
def txt_to_obj(txt):
    base64_bytes = txt.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    obj = pickle.loads(message_bytes)
    return obj

def dump(obj):
    display(repr(obj))
    for attr in dir(obj):
        if not attr.startswith("__"):
            display(attr + " = " + repr(getattr(obj, attr)))
