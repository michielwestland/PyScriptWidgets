"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


from typing import Self

from widgets.base import PBaseWidget


class PCompoundWidget(PBaseWidget):
    """Abstract compound widget base class, that can have children"""

    def __init__(self, tag: str):
        """Constructor, define tag and class attributes"""
        super().__init__(tag)
        # Children
        self._children = []
        # Properties
        self._margin = None
        self._render_margin()
        self._border_width = None
        self._render_border_width()
        self._border_style = ""
        self._render_border_style()
        self._border_color = ""
        self._render_border_color()
        self._padding = None
        self._render_padding()
        self._row_gap = 0
        self._render_row_gap()
        self._column_gap = 0
        self._render_column_gap()

    def find_id(self, widget_id: str) -> PBaseWidget | None:
        """Find a reference to the widget with this id, also search in children"""
        if self._widget_id == widget_id:
            return self
        for c in self._children:
            f = c.findId(widget_id)
            if f is not None:
                return f
        return None

    # Children
    def get_children(self) -> list[PBaseWidget]:
        """Get the list of children"""
        return self._children

    def remove_child(self, child: PBaseWidget) -> Self:
        """Remove a single child"""
        child._parent = None  # pylint: disable=protected-access
        self._elem.removeChild(child._elem)  # pylint: disable=protected-access
        self._children.remove(child)
        return self

    def remove_all_children(self) -> Self:
        """Remove all children"""
        self._elem.replaceChildren()
        for c in self._children:
            c._parent = None  # pylint: disable=protected-access
        self._children.clear()
        return self

    def add_child(self, child: PBaseWidget) -> Self:
        """Add a single child"""
        child._parent = self  # pylint: disable=protected-access
        child.set_dark_mode(
            child.get_parent().is_dark_mode()
        )  # Inherit dark mode property from parent
        self._elem.appendChild(child._elem)  # pylint: disable=protected-access
        self._children.append(child)
        return self

    def add_children(self, children: list[PBaseWidget]) -> Self:
        """Add a list of children"""
        for c in children:
            self.add_child(c)
        return self

    def backup_state(self):
        """Override this method to backup runtime DOM state to widget instance fields before pickling to session storage"""
        super().backup_state()
        for c in self._children:
            c.backup_state()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        for c in self._children:
            c.restore_state()
            c._parent = self  # pylint: disable=protected-access
            self._elem.appendChild(c._elem)  # pylint: disable=protected-access
        # Properties
        self._render_margin()
        self._render_border_width()
        self._render_border_style()
        self._render_border_color()
        self._render_padding()
        self._render_row_gap()
        self._render_column_gap()

    def after_page_load(self):
        """Override this method tot execute code after the page DOM has loaded"""
        super().after_page_load()
        for c in self._children:
            c.after_page_load()

    # Property: dark_mode (overridden)
    def set_dark_mode(self, dark_mode: bool):
        """Mutator"""
        super().set_dark_mode(dark_mode)
        for c in self._children:
            c.set_dark_mode(dark_mode)

    # Property: margin
    def _render_margin(self):
        """Renderer"""
        if self._margin is not None:
            try:
                pixels = int(self._margin)
                self._elem.style.margin = str(pixels) + "px"
            except ValueError:
                self._elem.style.margin = str(self._margin)  # It was not an integer value

    def get_margin(self) -> int | str | None:
        """Accessor"""
        return self._margin

    def set_margin(self, margin: int | str | None) -> Self:
        """Mutator"""
        if self._margin != margin:
            self._margin = margin
            self._render_margin()
        return self

    # Property: border_width
    def _render_border_width(self):
        """Renderer"""
        if self._border_width is not None:
            try:
                pixels = int(self._border_width)
                self._elem.style.borderWidth = str(pixels) + "px"
            except ValueError:
                self._elem.style.borderWidth = str(self._border_width)  # It was not an integer value

    def get_border_width(self) -> int | str | None:
        """Accessor"""
        return self._border_width

    def set_border_width(self, border_width: int | str | None) -> Self:
        """Mutator"""
        if self._border_width != border_width:
            self._border_width = border_width
            self._render_border_width()
        return self

    # Property: border_style
    def _render_border_style(self):
        """Renderer"""
        self._elem.style.borderStyle = self._border_style if self._border_style != "" else None

    def get_border_style(self) -> str:
        """Accessor"""
        return self._border_style

    def set_border_style(self, border_style: str) -> Self:
        """Mutator"""
        # Valid styles, see: https://www.w3schools.com/css/css_border.asp
        if self._border_style != border_style:
            self._border_style = border_style
            self._render_border_style()
        return self

    # Property: border_color
    def _render_border_color(self):
        """Renderer"""
        self._elem.style.borderColor = self._border_color if self._border_color != "" else None

    def get_border_color(self) -> str:
        """Accessor"""
        return self._border_color

    def set_border_color(self, border_color: str) -> Self:
        """Mutator"""
        if self._border_color != border_color:
            self._border_color = border_color
            self._render_border_color()
        return self

    # Property: padding
    def _render_padding(self):
        """Renderer"""
        if self._padding is not None:
            try:
                pixels = int(self._padding)
                self._elem.style.padding = str(pixels) + "px"
            except ValueError:
                self._elem.style.padding = str(self._padding)  # It was not an integer value

    def get_padding(self) -> int | str | None:
        """Accessor"""
        return self._padding

    def set_padding(self, padding: int | str | None) -> Self:
        """Mutator"""
        if self._padding != padding:
            self._padding = padding
            self._render_padding()
        return self

    # Property: row_gap
    def _render_row_gap(self):
        """Renderer"""
        self._elem.style.rowGap = str(self._row_gap) + "px"

    def get_row_gap(self) -> int:
        """Accessor"""
        return self._row_gap

    def set_row_gap(self, row_gap: int):
        """Mutator"""
        if self._row_gap != row_gap:
            self._row_gap = row_gap
            self._render_row_gap()
        return self

    # Property: column_gap
    def _render_column_gap(self):
        """Renderer"""
        self._elem.style.columnGap = str(self._column_gap) + "px"

    def get_column_gap(self) -> int:
        """Accessor"""
        return self._column_gap

    def set_column_gap(self, column_gap: int):
        """Mutator"""
        if self._column_gap != column_gap:
            self._column_gap = column_gap
            self._render_column_gap()
        return self
