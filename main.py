from datetime import datetime
from js import console, document, sessionStorage, fetch, JSON, window
from pyodide.ffi import create_proxy
from pyscript import display

txIn = None
time = ""

def dump(obj):
    display("=" * 80)
    display(repr(obj))
    for attr in dir(obj):
        display(attr + " = " + repr(getattr(obj, attr)))

def action(*args):
    #console.log(repr(args))
    global time
    time = str(datetime.now())
    sessionStorage.setItem("now", time) # store the class tree using JSON.stringify(data)
    txIn.value = "Now is: " + time

def main():
    root = document.getElementById("root")

    global txIn
    txIn = document.createElement("input")
    txIn.setAttribute("placeholder", "press this button -->") # attribute
    txIn.setAttribute("style", "width: 300px")
    root.appendChild(txIn)
    #dump(txIn)

    btn = document.createElement("button")
    btn.appendChild(document.createTextNode("Press me!")) # text
    btn.addEventListener("click", create_proxy(action)) # event
    btn.setAttribute("style", "color: red")
    root.appendChild(btn)

    t = sessionStorage.getItem("now") # load the class tree using JSON.parse(data)
    if t != None:
        time = t
        txIn.value = "Loaded: " + time

if __name__ == "__main__":
    main()
