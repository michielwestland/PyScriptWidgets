from datetime import datetime
from js import fetch, JSON # type: ignore
from widgets import PPanel, PGrid, PTextInput, PButton, PLabel, bindToDom
from todo import TodoPanel

class Main(PPanel):

    def __init__(self):
        super().__init__(True)
        self.inp = PTextInput("").setPlaceholder("press the button...")
        self.btn = PButton("Press me!").setColor("blue").onClick(self.btnClick)

        self.grd = PGrid().setMargin(6).setGap(6)
        self.grd.setRows(["36px", "36px", "72px"])
        self.grd.setColumns(["100px", "200px", "100px", "200px"])
        self.grd.setAreas([
            [PLabel("Code")       , PTextInput("<code>"), PLabel("Number"), PTextInput("<number>")], 
            [PLabel("Description"), self.inp            , self.inp        , self.inp              ], 
            [None                 , None                , self.btn        , self.btn              ],
        ])
        self.addChild(self.grd)

        self.todoPnl = TodoPanel()
        self.addChild(self.todoPnl)

    async def btnClick(self, event): 
        self.btn.setColor("red")
        response = await fetch("/PyScriptWidgets/data.json", {"method": "GET"})
        data = await response.json()
        self.inp.setValue("Now is: " + str(datetime.now()) + " " + JSON.stringify(data))

    def afterPageLoad(self):
        super().afterPageLoad()
        # Hier kan je code uitproberen na page refresh i.c.m. Live Server/Live Preview
        self.btn.setColor("green")

if __name__ == "__main__":
    bindToDom(Main, "root")
