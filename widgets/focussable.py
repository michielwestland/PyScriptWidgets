"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


from widgets.base import PWidget


class PFocussableWidget(PWidget):
    """Abstract focussable widget class"""

    def __init__(self, tag):
        """Constructor, define tag and class attributes"""
        super().__init__(tag)
        # Properties
        self._enabled = True
        self._render_enabled()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_enabled()

    def request_focus(self):
        """Request the input focus and scroll the widget into view"""
        self._elem.scrollIntoView()
        self._elem.focus()

    # Property: enabled
    def _render_enabled(self):
        """Renderer"""
        if self._enabled:
            self._elem.removeAttribute("disabled")
        else:
            self._elem.setAttribute("disabled", "")

    def is_enabled(self):
        """Accessor"""
        return self._enabled

    def set_enabled(self, enabled):
        """Mutator"""
        if self._enabled != enabled:
            self._enabled = enabled
            self._render_enabled()
        return self
