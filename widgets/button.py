"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


# Prefer pyscript import over more basic js import for the document and window objects
from pyscript import document  # type: ignore # pylint: disable=import-error
from pyodide.ffi.wrappers import add_event_listener, remove_event_listener  # type: ignore # pylint: disable=import-error

from widgets.focussable import PFocussableWidget
from widgets.globals import _ID_SUPPLEMENT


class PButton(PFocussableWidget):
    """Button widget class"""

    # See: https://fomantic-ui.com/kitchen-sink.html
    def __init__(self, text):
        """Constructor, define tag and class attributes"""
        super().__init__("button")
        self._elem.classList.add("button")
        # Properties
        self._text = text
        self._icon = ""
        self._render_text_icon()
        self._click = None
        self._render_click()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_text_icon()
        self._render_click()

    # Property: text
    def _render_text_icon(self):
        """Renderer"""
        self._elem.replaceChildren()
        if len(self._icon) > 0:
            e = document.createElement("i")
            e.id = self._widget_id + _ID_SUPPLEMENT + "i"
            e.classList.add("icon")
            for c in self._icon.split():
                e.classList.add(c)
            self._elem.appendChild(e)
        s = " " if len(self._icon) > 0 and len(self._text) > 0 else ""
        if len(s + self._text) > 0:
            self._elem.appendChild(document.createTextNode(s + self._text))

    def get_text(self):
        """Accessor"""
        return self._text

    def set_text(self, text):
        """Mutator"""
        if self._text != text:
            self._text = text
            self._render_text_icon()
        return self

    # Property: icon
    def get_icon(self):
        """Accessor"""
        return self._icon

    def set_icon(self, icon):
        """Mutator"""
        if self._icon != icon:
            self._icon = icon
            self._render_text_icon()
        return self

    # Property: click (writeonly)
    def _render_click(self):
        """Renderer"""
        if self._click is not None:
            add_event_listener(self._elem, "click", self._click)

    def on_click(self, click):
        """Mutator"""
        if id(self._click) != id(click):  # Object reference/id comparison
            if self._click is not None:
                remove_event_listener(self._elem, "click", self._click)
            self._click = click
            self._render_click()
        return self
