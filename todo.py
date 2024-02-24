"""Todo example"""

from datetime import datetime
from widgets import PPanel, PLabel, PTextInput, PButton

class TodoForm(PPanel):
    """Todo form containing item add/entry fields"""

    def __init__(self):
        super().__init__(False)
        self.setGap(5)
        self.inp = PTextInput("").setPlaceholder("<new todo>")
        self.add_btn = PButton("Add").onClick(self.add_btn_click)
        self.addChildren([self.inp, self.add_btn])

    def add_btn_click(self, event): # pylint: disable=unused-argument
        """Ädd button event handler"""
        text = self.inp.getValue()
        if len(text) == 0:
            text = "<" + str(datetime.now()) + ">"
        self.getParent().lst.addChild(TodoItem(text))
        self.inp.setValue("")

class TodoItem(PPanel):
    """Todo item containing item delete/display fields"""

    def __init__(self, todoTxt):
        super().__init__(False)
        self.setGap(5)
        self.lbl = PLabel(todoTxt)
        # See: https://semantic-ui.com/elements/icon.html
        self.delete_btn = PButton("Delete") \
                .setIcon("trash alternate") \
                .onClick(self.delete_btn_click)
        self.addChildren([self.delete_btn, self.lbl])

    def delete_btn_click(self, event): # pylint: disable=unused-argument
        """Delete button event handler"""
        self.getParent().getParent().frm.inp.requestFocus()
        self.getParent().removeChild(self)

class TodoList(PPanel):
    """Todo list containing items"""

    def __init__(self):
        super().__init__(True)
        self.setGap(5)

class TodoPanel(PPanel):
    """Todo panel containing form and list"""

    def __init__(self):
        super().__init__(True)
        self.setMargin(5)
        self.frm = TodoForm()
        self.lst = TodoList()
        self.addChildren([
            PLabel("Todo form:"),
            self.frm,
            PLabel("Todo list:"),
            self.lst,
        ])
