import asyncio
import extra
from datetime import datetime
from js import window, sessionStorage, fetch, JSON # type: ignore
from pyodide.ffi import create_proxy # type: ignore
from widgets import PPanel, PEdit, PButton, PLabel

app = None

async def btn_click(event): 
    pnl = app.findTarget(event).getParent()
    pnl.btn.setColor("red")
    time = str(datetime.now())
    
    response = await fetch("data.json", {"method": "GET"})
    data = await response.json()
    time = time + " " + JSON.stringify(data)
    
    pnl.edt.setValue("Now is: " + time)

class App(PPanel):

    def __init__(self, rootElementId):
        super().__init__(rootElementId)

        lbl = PLabel("Label") #TODO Maak onderscheid tussen design attributen die je (niet/soms) wilt backuppen en runtime attributem die je altijd backupt
        self.addChild(lbl)

        self.edt = PEdit("").setPlaceholder("press this button -->").setWidth(500)
        self.addChild(self.edt)

        self.btn = PButton("Press me!").setColor("blue").onClick(btn_click)
        self.addChild(self.btn)

async def window_beforeunload(*args):
    app.backupState()
    domState = extra.obj2txt(app)
    sessionStorage.setItem("domState", domState)

async def main():
    global app
    domState = sessionStorage.getItem("domState")
    if domState == None:
        app = App("root")
    else:
        app = extra.txt2obj(domState)
        app.restoreState()
    window.addEventListener("beforeunload", create_proxy(window_beforeunload))

if __name__ == "__main__":
    asyncio.ensure_future(main())
