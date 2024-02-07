from datetime import datetime
from js import fetch, JSON # type: ignore
from widgets import PPanel, PGrid, PTextInput, PButton, PLabel, bindToDom
from todo import TodoPanel

# Set the base url when deploying to: https://michielwestland.github.io/PyScriptWidgets
BASE_URL = "."

class Main(PPanel):

    def __init__(self):
        super().__init__(True)
        self.inp = PTextInput("").setPlaceholder("press the button...")
        self.btn = PButton("Press me!").setColor("blue").onClick(self.btnClick)

        self.grd = PGrid().setMargin(6).setGap(6)
        #TODO Can you use just integers, besides strings, and translate integer 999 to 999px internally?
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
        response = await fetch("./data.json", {"method": "GET"})
        data = await response.json()
        self.inp.setValue("Now is: " + str(datetime.now()) + " " + JSON.stringify(data))

    def afterPageLoad(self):
        super().afterPageLoad()
        # Here, try out code after a page refresh with Live Server/Live Preview
        self.btn.setColor("green")

if __name__ == "__main__":
    bindToDom(Main, "root")
