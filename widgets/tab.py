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


class PTab(PCompoundWidget):
    """Tabs widget class"""

    def __init__(self):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        self._insert_div()
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
        self._elem_div.classList.add("top attached tabular menu " + self.__class__.__name__)
        self._elem.appendChild(self._elem_div)

    def _insert_state(self):
        """Override this method to insert state, for keys that could not be pickled"""
        super()._insert_state()
        self._insert_div()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_active()

    # Property: active
    def _render_active(self):
        """Renderer"""
        #self._elem_input.setAttribute("type", self._input_type)

    def get_active(self) -> int:
        """Accessor"""
        return self._active

    def set_active(self, active: int) -> Self:
        """Mutator"""
        if self._active != active:
            self._active = active
            self._render_active()
        return self
