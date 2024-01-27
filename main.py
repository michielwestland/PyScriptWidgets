from datetime import datetime
from js import fetch, JSON # type: ignore
from widgets import PPanel, PGrid, PEdit, PButton, PLabel, bindToDom, findEventTarget
from todo import TodoPanel

async def btn_click(event): 
    grd = findEventTarget(event).getParent()
    pnl = grd.getParent()
    
    pnl.btn.setColor("red")
    time = str(datetime.now())
    
    response = await fetch("data.json", {"method": "GET"})
    data = await response.json()
    time = time + " " + JSON.stringify(data)
    
    pnl.edt.setValue("Now is: " + time)

class Main(PPanel):

    def __init__(self):
        super().__init__(True)

        self.edt = PEdit("").setPlaceholder("press the button...").setWidth(400)
        self.btn = PButton("Press me!").setColor("blue").onClick(btn_click)

        self.grd = PGrid().setMargin(10).setGap(5)
        self.grd.setRows(["20px", "20px", "50px"])
        self.grd.setColumns(["100px", "150px", "100px", "150px"])
        self.grd.setAreas([
            [PLabel("Code")       , PEdit("<code>"), PLabel("Number"), PEdit("<number>")], 
            [PLabel("Description"), self.edt       , self.edt        , self.edt         ], 
            [None                 , None           , self.btn        , self.btn         ]
        ])
        self.addChild(self.grd)

        self.todoPnl = TodoPanel()
        self.addChild(self.todoPnl)

    def afterPageLoad(self):
        super().afterPageLoad()
        # Hier kan je code uitproberen na page refresh i.c.m. LiveServer
        #self.btn.setColor("green")

if __name__ == "__main__":
    bindToDom(Main, "root")
