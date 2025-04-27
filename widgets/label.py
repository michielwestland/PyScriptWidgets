"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


# Prefer pyscript import over more basic js import for the document and window objects
from pyscript import document  # type: ignore # pylint: disable=import-error


from widgets.focussable import PFocussableWidget
from widgets.globals import _ID_SUPPLEMENT
from widgets.input import PInputWidget


class PLabel(PFocussableWidget):
    """Label widget class"""

    def __init__(self, text):
        """Constructor, define tag and class attributes"""
        super().__init__("label")
        # Properties
        self._text = text
        self._render_text()
        self._for = None
        self._render_for()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_text()
        self._render_for()

    # Property: text
    def _render_text(self):
        """Renderer"""
        self._elem.replaceChildren(document.createTextNode(self._text))

    def get_text(self):
        """Accessor"""
        return self._text

    def set_text(self, text):
        """Mutator"""
        if self._text != text:
            self._text = text
            self._render_text()
        return self

    # Property: for
    def _render_for(self):
        """Renderer"""
        if self._for is None:
            self._elem.removeAttribute("for")
        else:
            if isinstance(self._for, PInputWidget):
                self._elem.htmlFor = (
                    self._for._widget_id  # pylint: disable=protected-access
                    + _ID_SUPPLEMENT
                    + "input"
                )
            else:
                self._elem.htmlFor = self._for._widget_id  # pylint: disable=protected-access

    def get_for(self):
        """Accessor"""
        return self._for

    def set_for(self, for_widget):
        """Mutator"""
        if id(self._for) != id(for_widget):  # Object reference/id comparison
            self._for = for_widget
            self._render_for()
        return self
