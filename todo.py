"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

Todo example
"""

from datetime import datetime
from widgets import PPanel, PLabel, PTextInput, PButton


class TodoForm(PPanel):
    """Todo form containing item add/entry fields"""

    def __init__(self):
        super().__init__(False)
        self.set_row_gap(5).set_column_gap(5)
        self.inp = PTextInput("").set_placeholder("<new todo>")
        self.add_btn = PButton("Add").on_click(self.add_btn_click)
        self.add_children([self.inp, self.add_btn])

    def add_btn_click(self, event):  # pylint: disable=unused-argument
        """Add button event handler"""
        text = self.inp.get_value()
        if len(text) == 0:
            text = "<" + str(datetime.now()) + ">"
        self.get_parent().lst.add_child(TodoItem(text))
        self.inp.set_value("")


class TodoItem(PPanel):
    """Todo item containing item delete/display fields"""

    def __init__(self, todoTxt):
        super().__init__(False)
        self.set_row_gap(5).set_column_gap(5)
        self.lbl = PLabel(todoTxt)
        self.delete_btn = (
            PButton("Delete").set_icon("trash alternate").on_click(self.delete_btn_click)
        )
        self.add_children([self.delete_btn, self.lbl])

    def delete_btn_click(self, event):  # pylint: disable=unused-argument
        """Delete button event handler"""
        self.get_parent().get_parent().frm.inp.request_focus()
        self.get_parent().remove_child(self)


class TodoList(PPanel):
    """Todo list containing items"""

    def __init__(self):
        super().__init__(True)
        self.set_row_gap(5).set_column_gap(5)


class TodoPanel(PPanel):
    """Todo panel containing form and list"""

    def __init__(self):
        super().__init__(True)
        self.set_margin(5)
        self.frm = TodoForm()
        self.lst = TodoList()
        self.add_children(
            [
                PLabel("Todo form:"),
                self.frm,
                PLabel("Todo list:"),
                self.lst,
            ]
        )
