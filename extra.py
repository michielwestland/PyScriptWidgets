import pickle
import base64
from pyscript import display

# See: https://oren-sifri.medium.com/serializing-a-python-object-into-a-plain-text-string-7411b45d099e

# Serialize an object into a plain text
def obj2txt(obj):
    raw_bytes = pickle.dumps(obj)
    base64_bytes = base64.b64encode(raw_bytes)
    txt = base64_bytes.decode("utf-8")
    return txt

# De-serialize an object from a plain text
def txt2obj(txt):
    base64_bytes = txt.encode("utf-8")
    raw_bytes = base64.b64decode(base64_bytes)
    obj = pickle.loads(raw_bytes)
    return obj

def dump(obj):
    display(repr(obj))
    for attr in dir(obj):
        if not attr.startswith("__"):
            display(attr + " = " + repr(getattr(obj, attr)))
