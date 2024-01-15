import asyncio
import extra
from datetime import datetime
from js import console, document, sessionStorage, fetch, JSON, window
from pyodide.ffi import create_proxy

async def main():
    time = ""
    root = document.getElementById("root")

    txIn = document.createElement("input")
    txIn.setAttribute("placeholder", "press this button -->") # attribute
    txIn.setAttribute("style", "width: 500px") # css
    root.appendChild(txIn)
    extra.dump(txIn)

    btn = document.createElement("button")
    btn.appendChild(document.createTextNode("Press me!")) # text
    async def btn_click(*args): # event handler
        btn.setAttribute("style", "color: red")
        console.log(repr(args))
        time = str(datetime.now())

        response = await fetch("data.json", {"method": "GET"}) # webservice request
        data = await response.json()
        time = time + " " + JSON.stringify(data)

        sessionStorage.setItem("now", time) # serialize the class tree using JSON.stringify(data)
        txIn.value = "Now is: " + time

    btn.addEventListener("click", create_proxy(btn_click)) # event
    root.appendChild(btn)

    t = sessionStorage.getItem("now") # de-serialize the class tree using JSON.parse(data)
    if t != None:
        time = t
        txIn.value = "Loaded: " + time

if __name__ == "__main__":
    asyncio.ensure_future(main())
