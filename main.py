import asyncio
import extra
from datetime import datetime
from js import console, sessionStorage, fetch, JSON # type: ignore
from widgets import PPanel, PEdit, PButton, PLabel

async def main():
    time = ""

    root = PPanel("root").addChild(PLabel("Label"))

    txIn = PEdit("").setPlaceholder("press this button -->") \
        .setWidth(500)
    #extra.dump(txIn)
    root.addChild(txIn)

    btn = PButton("Press me!").setColor("blue")
    async def btn_click(*args): # event handler
        btn.setColor("red")
        console.log(repr(args))
        time = str(datetime.now())
        #
        response = await fetch("data.json", {"method": "GET"}) # webservice request
        data = await response.json()
        time = time + " " + JSON.stringify(data)
        #
        sessionStorage.setItem("now", time) #TODO serialize the class tree using JSON.stringify(data)
        txIn.setValue("Now is: " + time)
    btn.onClick(btn_click)
    root.addChild(btn)

    t = sessionStorage.getItem("now") #TODO de-serialize the class tree using JSON.parse(data)
    if t != None:
        time = t
        txIn.setValue("Loaded: " + time)

if __name__ == "__main__":
    asyncio.ensure_future(main())
