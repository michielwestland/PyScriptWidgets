from datetime import datetime
from js import console, document, sessionStorage, fetch, JSON, window
from pyodide.ffi import create_proxy
from pyscript import display

def dump(obj):
    display(repr(obj))
    for attr in dir(obj):
        if attr.startswith("v"):
            display(attr + " = " + repr(getattr(obj, attr)))

def main():
    time = ""
    root = document.getElementById("root")

    txIn = document.createElement("input")
    txIn.setAttribute("placeholder", "press this button -->") # attribute
    txIn.setAttribute("style", "width: 300px")
    root.appendChild(txIn)
    dump(txIn)

    btn = document.createElement("button")
    btn.appendChild(document.createTextNode("Press me!")) # text
    def btn_click(*args):
        console.log(repr(args))
        time = str(datetime.now())
        sessionStorage.setItem("now", time) # serialize the class tree using JSON.stringify(data)
        txIn.value = "Now is: " + time
    btn.addEventListener("click", create_proxy(btn_click)) # event
    btn.setAttribute("style", "color: red")
    root.appendChild(btn)

    t = sessionStorage.getItem("now") # de-serialize the class tree using JSON.parse(data)
    if t != None:
        time = t
        txIn.value = "Loaded: " + time

if __name__ == "__main__":
    main()
