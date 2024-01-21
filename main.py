from datetime import datetime
from js import fetch, JSON # type: ignore
from widgets import PPanel, PEdit, PButton, PLabel, bindToDom, findEventTarget

async def btn_click(event): 
    pnl = findEventTarget(event).getParent()
    pnl.btn.setColor("red")
    time = str(datetime.now())
    
    response = await fetch("data.json", {"method": "GET"})
    data = await response.json()
    time = time + " " + JSON.stringify(data)
    
    pnl.edt.setValue("Now is: " + time)

class Main(PPanel):

    def __init__(self):
        super().__init__()

        lbl = PLabel("Label")
        self.addChild(lbl)

        self.edt = PEdit("").setPlaceholder("press this button -->").setWidth(500)
        self.addChild(self.edt)

        self.btn = PButton("Press me!").setColor("blue").onClick(btn_click)
        self.addChild(self.btn)

    def restoreState(self):
        super().restoreState()
        
        # Hier kan je iets uitproberen i.c.m. live server
        self.btn.setColor("green")

if __name__ == "__main__":
    bindToDom(Main, "root")
