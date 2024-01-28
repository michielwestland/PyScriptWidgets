from datetime import datetime
from widgets import PPanel, PLabel, PTextInput, PButton, findEventTarget

class TodoForm(PPanel):
    def __init__(self):
        super().__init__(False)
        self.inp = PTextInput("").setPlaceholder("<new todo>")
        self.addBtn = PButton("Add").onClick(self.addBtnClick)
        self.addChildren([self.inp, self.addBtn])

    def addBtnClick(self, event):
        text = self.inp.getValue()
        if len(text) == 0:
            text = "<" + str(datetime.now()) + ">"
        self.getParent().lst.addChild(TodoItem(text))
        self.inp.setValue("")

class TodoItem(PPanel):
    def __init__(self, todoTxt):
        super().__init__(False)
        self.lbl = PLabel(todoTxt)
        self.deleteBtn = PButton("Delete").setIcon("fa-solid fa-trash-can").onClick(self.deleteBtnClick)
        self.addChildren([self.deleteBtn, self.lbl])

    def deleteBtnClick(self, event):
        self.getParent().removeChild(self)

class TodoList(PPanel):
    def __init__(self):
        super().__init__(True)
        self.setGap(5)

class TodoPanel(PPanel):
    def __init__(self):
        super().__init__(True)
        self.setMargin(20)
        self.frm = TodoForm()
        self.lst = TodoList()
        self.addChildren([
            PLabel("Todo form:"),
            self.frm,
            PLabel("Todo list:"),
            self.lst,
        ])
