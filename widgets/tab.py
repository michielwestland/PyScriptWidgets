"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""

from typing import Self

# Prefer pyscript import over more basic js import for the document and window objects
from pyscript import document  # type: ignore # pylint: disable=import-error

from widgets.compound import PCompoundWidget
from widgets.globals import _ID_SUPPLEMENT


_ID_DIV = "div"
_ID_A = "a"


class PTab(PCompoundWidget):
    """Tabs widget class"""

    def __init__(self):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        self._insert_div()
        # Tabs
        self._elem_tabs = []
        self._tabs = []
        # Properties
        self._active = -1  # no tab selected
        self._render_active()

    def _delete_state(self, state):
        """Override this method to delete state keys that cannot be pickled"""
        super()._delete_state(state)
        del state["_elem_div"]

    def _insert_div(self):
        """Insert the inner div element into the DOM tree"""
        # No need to replace existing children, this method is only called from initialization or deserialization
        # See: https://fomantic-ui.com/modules/tab.html#/examples
        self._elem_div = document.createElement("div")
        self._elem_div.id = self._widget_id + _ID_SUPPLEMENT + _ID_DIV
        #self._elem_div.classList.add(self.__class__.__name__)
        self._elem_div.classList.add("top")
        self._elem_div.classList.add("attached")
        self._elem_div.classList.add("tabular")
        self._elem_div.classList.add("menu")
        self._elem.appendChild(self._elem_div)

    def _insert_state(self):
        """Override this method to insert state, for keys that could not be pickled"""
        super()._insert_state()
        self._insert_div()

    # Tabs
    def get_tabs(self) -> list[str]:
        """Get the list of tabs"""
        return self._tabs

    def remove_all_tabs(self) -> Self:
        """Remove all tabs"""
        self._elem_div.replaceChildren()
        self._elem_tabs.clear()
        self._tabs.clear()
        return self

    def add_tab(self, tab: str) -> Self:
        """Add a single tab"""
        elem_a = document.createElement("a")
        elem_a.id = self._widget_id + _ID_SUPPLEMENT + _ID_DIV + _ID_SUPPLEMENT + _ID_A + str(len(self._tabs))
        #elem_a.classList.add(self.__class__.__name__)
        elem_a.classList.add("item")
        elem_a.dataset.tab = len(self._tabs)
        elem_a.replaceChildren(document.createTextNode(tab))
        self._elem_div.appendChild(elem_a)

        self._elem_tabs.append(elem_a)
        self._tabs.append(tab)
        return self

    def backup_state(self):
        """Override this method to backup runtime DOM state to widget instance fields before pickling to session storage"""
        super().backup_state()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        #for c in self._children:
        #    c.restore_state()
        #    c._parent = self  # pylint: disable=protected-access
        #    self._elem.appendChild(c._elem)  # pylint: disable=protected-access
        # Properties
        self._render_active()

    # Property: active
    def _render_active(self):
        """Renderer"""
        for e in self._elem_tabs:
            e.classList.remove("active")
        if self._active > 0 and self._active < len(self._elem_tabs):
            self._elem_tabs[self._active].classList.add("active")

    def get_active(self) -> int:
        """Accessor"""
        return self._active

    def set_active(self, active: int) -> Self:
        """Mutator"""
        if self._active != active:
            self._active = active
            self._render_active()
        return self
