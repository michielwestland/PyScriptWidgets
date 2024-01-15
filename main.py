import asyncio
import extra
from datetime import datetime
from js import console, document, sessionStorage, fetch, JSON, window # type: ignore
from widgets import PButton, PEdit

async def main():
    time = ""
    root = document.getElementById("root")

    txIn = PEdit("")
    txIn.setPlaceholder("press this button -->")
    txIn.setWidth(500)
    root.appendChild(txIn._elem)

    extra.dump(txIn)

    btn = PButton("Press me!")
    async def btn_click(*args): # event handler
        btn.setColor("red")
        console.log(repr(args))
        time = str(datetime.now())

        response = await fetch("data.json", {"method": "GET"}) # webservice request
        data = await response.json()
        time = time + " " + JSON.stringify(data)

        sessionStorage.setItem("now", time) #TODO serialize the class tree using JSON.stringify(data)
        txIn.setValue("Now is: " + time)

    btn.onClick(btn_click)
    root.appendChild(btn._elem)

    t = sessionStorage.getItem("now") #TODO de-serialize the class tree using JSON.parse(data)
    if t != None:
        time = t
        txIn.setValue("Loaded: " + time)

if __name__ == "__main__":
    asyncio.ensure_future(main())
