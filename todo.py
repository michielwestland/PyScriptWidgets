from datetime import datetime
from widgets import PPanel, PLabel, PEdit, PButton, findEventTarget

def add_btn_click(event):
    pnl = findEventTarget(event).getParent().getParent()
    
    text = pnl.frm.edt.getValue()
    if len(text) == 0:
        text = "<" + str(datetime.now()) + ">"
    
    item = TodoItem(text)
    pnl.lst.addChild(item)

    pnl.frm.edt.setValue("")

def delete_btn_click(event):
    item = findEventTarget(event).getParent()
    
    lst = item.getParent()
    lst.removeChild(item)

class TodoForm(PPanel):

    def __init__(self):
        super().__init__(False)

        self.edt = PEdit("").setPlaceholder("<new todo>").setWidth(300)
        self.addChild(self.edt)

        self.addBtn = PButton("Add").onClick(add_btn_click)
        self.addChild(self.addBtn)

class TodoItem(PPanel):

    def __init__(self, todoTxt):
        super().__init__(False)

        self.lbl = PLabel(todoTxt)
        self.addChild(self.lbl)

        self.deleteBtn = PButton("Delete").onClick(delete_btn_click)
        self.addChild(self.deleteBtn)

class TodoList(PPanel):

    def __init__(self):
        super().__init__(True)

        #self.itm = TodoItem("Todo 1")
        #self.addChild(self.itm)
        #
        #self.itm2 = TodoItem("Todo 2")
        #self.addChild(self.itm2)
        #
        #self.itm3 = TodoItem("Todo 3")
        #self.addChild(self.itm3)

class TodoPanel(PPanel):

    def __init__(self):
        super().__init__(True)

        self.addChild(PLabel("Todo list example:"))

        self.frm = TodoForm()
        self.addChild(self.frm)

        self.lst = TodoList()
        self.addChild(self.lst)
