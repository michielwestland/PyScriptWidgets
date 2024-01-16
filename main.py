import asyncio
import extra
from datetime import datetime
from js import console, window, sessionStorage, fetch, JSON # type: ignore
from pyodide.ffi import create_proxy # type: ignore
from pyscript import display
from widgets import PPanel, PEdit, PButton, PLabel

class App(PPanel):

    def __init__(self, rootElementId):
        super().__init__(rootElementId)

        self.addChild(PLabel("Label"))

        txIn = PEdit("").setPlaceholder("press this button -->").setWidth(500)
        self.addChild(txIn)

        btn = PButton("Press me!").setColor("blue")
        async def btn_click(*args): 
            btn.setColor("red")
            console.log(repr(args))
            time = str(datetime.now())
            #
            response = await fetch("data.json", {"method": "GET"})
            data = await response.json()
            time = time + " " + JSON.stringify(data)
            #
            txIn.setValue("Now is: " + time)
            #
            #self.backupState()
            #domState = extra.obj2txt(self)
            #sessionStorage.setItem("domState", domState)
            #display(">>>backup (btn)")
        btn.onClick(btn_click)
        self.addChild(btn)

    def _deleteState(self, state):
        super()._deleteState(state)
        #TODO Solve this error!!!
        #        
        # pyodide.asm.js:9 Uncaught (in promise) PythonError: Traceback (most recent call last):
        #   File "<exec>", line 72, in btn_click
        #   File "/home/pyodide/extra.py", line 9, in obj2txt
        #     raw_bytes = pickle.dumps(obj)
        #                 ^^^^^^^^^^^^^^^^^
        # AttributeError: Can't pickle local object 'App.__init__.<locals>.btn_click'
        #
        #del state["App.__init__.<locals>.btn_click"]

async def main():
    domState = sessionStorage.getItem("domState")
    if domState == None:
        app = App("root")
        extra.dump(app)
        display(">>>created")
    else:
        app = extra.txt2obj(domState)
        app.restoreState()
        extra.dump(app)
        display(">>>restored")
    #async def window_beforeunload(*args):
    #    app.backupState()
    #    domState = extra.obj2txt(app)
    #    sessionStorage.setItem("domState", domState)
    #    display(">>>backup (beforeunload)")
    #window.addEventListener("beforeunload", create_proxy(window_beforeunload))

if __name__ == "__main__":
    asyncio.ensure_future(main())
