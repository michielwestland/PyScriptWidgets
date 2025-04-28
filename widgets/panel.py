"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""

from typing import Self

from widgets.compound import PCompoundWidget


class PPanel(PCompoundWidget):
    """Panel widget class with flex layout"""

    def __init__(self, vertical: bool):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        self._insert_display()
        # Properties
        self._vertical = vertical
        self._render_vertical()
        self._wrap = False
        self._render_wrap()

    def _insert_state(self):
        """Override this method to insert state, for keys that could not be pickled"""
        super()._insert_state()
        self._insert_display()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_vertical()
        self._render_wrap()

    def _insert_display(self):
        # See: https://flexbox.malven.co
        self._elem.style.display = "flex"
        self._elem.style.alignItems = "baseline"

    # Property: vertical
    def _render_vertical(self):
        """Renderer"""
        self._elem.style.flexDirection = "column" if self._vertical else "row"

    def is_vertical(self) -> bool:
        """Accessor"""
        return self._vertical

    def set_vertical(self, vertical: bool) -> Self:
        """Mutator"""
        if self._vertical != vertical:
            self._vertical = vertical
            self._render_vertical()
        return self

    # Property: wrap
    def _render_wrap(self):
        """Renderer"""
        self._elem.style.flexWrap = "wrap" if self._wrap else "nowrap"

    def is_wrap(self) -> bool:
        """Accessor"""
        return self._wrap

    def set_wrap(self, wrap: bool) -> Self:
        """Mutator"""
        if self._wrap != wrap:
            self._wrap = wrap
            self._render_wrap()
        return self
