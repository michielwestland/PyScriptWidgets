"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


from collections.abc import Callable
from typing import Self

# Prefer pyscript import over more basic js import for the document and window objects
from pyscript import document  # type: ignore # pylint: disable=import-error
from pyodide.ffi.wrappers import add_event_listener, remove_event_listener  # type: ignore # pylint: disable=import-error

from widgets.focussable import PFocussableWidget
from widgets.globals import _ID_SUPPLEMENT


_ID_INPUT = "input"


class PInputWidget(PFocussableWidget):
    """Abstract input widget class with value and shared functionality"""

    def __init__(self, input_type: str, value: str):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        self._elem.classList.add("input")
        self._insert_input()
        # Value
        self._value = ""
        self.set_value(value)
        # Properties
        self._input_type = input_type
        self._render_input_type()
        self._enabled = True
        self._render_enabled()
        self._required = ""
        self._render_required()
        self._readonly = False
        self._render_readonly()
        self._change = None
        self._render_change()

    def backup_state(self):
        """Override this method to backup runtime DOM state to widget instance fields before pickling to session storage"""
        super().backup_state()
        self._value = self._elem_input.value

    def _delete_state(self, state):
        """Override this method to delete state keys that cannot be pickled"""
        super()._delete_state(state)
        del state["_elem_input"]

    def _insert_input(self):
        # Non need to replace existing children, this method is only called from initialization or deserialization
        self._elem_input = document.createElement("input")
        self._elem_input.setAttribute("type", "text")
        self._elem_input.id = self._widget_id + _ID_SUPPLEMENT + _ID_INPUT
        self._elem_input.classList.add(self.__class__.__name__)
        self._elem.appendChild(self._elem_input)

    def _insert_state(self):
        """Override this method to insert state, for keys that could not be pickled"""
        super()._insert_state()
        self._insert_input()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Value
        self.set_value(self._value)
        # Properties
        self._render_input_type()
        self._render_enabled()
        self._render_required()
        self._render_readonly()
        self._render_change()

    def request_focus(self):
        self._elem_input.scrollIntoView()
        self._elem_input.focus()

    # Value
    def get_value(self) -> str:
        """Accessor"""
        return self._elem_input.value

    def set_value(self, value: str) -> Self:
        """Mutator"""
        if self._elem_input.value != value:
            self._elem_input.value = value
        return self

    # Property: input_type
    def _render_input_type(self):
        """Renderer"""
        self._elem_input.setAttribute("type", self._input_type)

    def get_input_type(self) -> str:
        """Accessor"""
        return self._input_type

    def set_input_type(self, input_type: str) -> Self:
        """Mutator"""
        if self._input_type != input_type:
            self._input_type = input_type
            self._render_input_type()
        return self

    # Property: enabled (overridden)
    def _render_enabled(self):
        """Renderer"""
        # No need to call super(), because the surrounding element cannot be disabled
        if hasattr(
            self, "_elem_input"
        ):  # This overridden method is also called earlier, before _elem_input exists
            if self._enabled:
                self._elem_input.removeAttribute("disabled")
            else:
                self._elem_input.setAttribute("disabled", "")

    # Property: required
    def _render_required(self):
        """Renderer"""
        if self._required:
            self._elem_input.setAttribute("required", "")
        else:
            self._elem_input.removeAttribute("required")

    def is_required(self) -> bool:
        """Accessor"""
        return self._required

    def set_required(self, required: bool) -> Self:
        """Mutator"""
        if self._required != required:
            self._required = required
            self._render_required()
        return self

    # Property: readonly
    def _render_readonly(self):
        """Renderer"""
        if self._readonly:
            self._elem_input.setAttribute("readonly", "")
        else:
            self._elem_input.removeAttribute("readonly")

    def is_readonly(self) -> bool:
        """Accessor"""
        return self._readonly

    def set_readonly(self, readonly: bool) -> Self:
        """Mutator"""
        if self._readonly != readonly:
            self._readonly = readonly
            self._render_readonly()
        return self

    # Property: change (writeonly)
    def _render_change(self):
        """Renderer"""
        if self._change is not None:
            add_event_listener(self._elem, "change", self._change)

    def on_change(self, change: Callable | None) -> Self:
        """Mutator"""
        if id(self._change) != id(change):  # Object reference/id comparison
            if self._change is not None:
                remove_event_listener(self._elem, "change", self._change)
            self._change = change
            self._render_change()
        return self
