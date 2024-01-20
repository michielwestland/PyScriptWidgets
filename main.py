from datetime import datetime
from js import console, fetch, JSON, sessionStorage, window # type: ignore
from pyodide.ffi import create_proxy # type: ignore
from widgets import PApplication, PEdit, PButton, PLabel, serializeWidgetsToBase64, deserializeWidgetsFromBase64

app = None

async def btn_click(event): 
    pnl = app.findTarget(event).getParent()
    pnl.btn.setColor("red")
    time = str(datetime.now())
    
    response = await fetch("data.json", {"method": "GET"})
    data = await response.json()
    time = time + " " + JSON.stringify(data)
    
    pnl.edt.setValue("Now is: " + time)

class App(PApplication):

    def __init__(self):
        super().__init__()

        lbl = PLabel("Label")
        self.addChild(lbl)

        self.edt = PEdit("").setPlaceholder("press this button -->").setWidth(500)
        self.addChild(self.edt)

        self.btn = PButton("Press me!").setColor("blue").onClick(btn_click)
        self.addChild(self.btn)

#TODO Maak onderscheid tussen design attributen die je (niet/soms) wilt backuppen en runtime attributen die je altijd backupt

def window_beforeunload(event):
    app.backupState()
    state = serializeWidgetsToBase64(app)
    sessionStorage.setItem("state", state)

def main():
    global app
    state = sessionStorage.getItem("state")
    if state == None:
        app = App()
        app.bindToDom("root")
    else:
        app = deserializeWidgetsFromBase64(state)
        app.restoreState()
        console.log("Application state restored from browser session storage")
    window.addEventListener("beforeunload", create_proxy(window_beforeunload))

if __name__ == "__main__":
    main()
