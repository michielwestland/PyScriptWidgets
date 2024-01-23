from datetime import datetime
from widgets import PPanel, PLabel, PEdit, PButton, findEventTarget

def add_btn_click(event):
    pnl = findEventTarget(event).getParent().getParent()
    text = pnl.frm.edt.getValue()
    if len(text) == 0:
        text = "<" + str(datetime.now()) + ">"
    pnl.lst.addChild(TodoItem(text))
    pnl.frm.edt.setValue("")

def delete_btn_click(event):
    item = findEventTarget(event).getParent()
    lst = item.getParent()
    lst.removeChild(item)

class TodoForm(PPanel):
    def __init__(self):
        super().__init__(False)
        self.edt = PEdit("").setPlaceholder("<new todo>").setWidth(300)
        self.addBtn = PButton("Add").onClick(add_btn_click)
        self.addChildren([self.edt, self.addBtn])

class TodoItem(PPanel):
    def __init__(self, todoTxt):
        super().__init__(False)
        self.lbl = PLabel(todoTxt)
        self.deleteBtn = PButton("Delete").setIcon("fa-solid fa-trash-can").onClick(delete_btn_click)
        self.addChildren([self.deleteBtn, self.lbl])

class TodoList(PPanel):
    def __init__(self):
        super().__init__(True)

class TodoPanel(PPanel):
    def __init__(self):
        super().__init__(True)
        self.frm = TodoForm()
        self.lst = TodoList()
        self.addChildren([
            PLabel("Todo form:"),
            self.frm,
            PLabel("Todo list:"),
            self.lst,
        ])
