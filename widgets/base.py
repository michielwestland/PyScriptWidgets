"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


from typing import Any, Self
# Prefer pyscript import over more basic js import for the document and window objects
from pyscript import document  # type: ignore # pylint: disable=import-error

from widgets.globals import _generate_unique_id, _ensure_unique_id_beyond


class PBaseWidget:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """Abstract widget base class"""

    def __init__(self, tag: str):
        """Constructor, define tag and class attributes"""
        self._tag = tag
        self._parent = None
        self._widget_id = _generate_unique_id()
        # DOM manipulation: https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model
        self._elem = document.createElement(self._tag)
        self._insert_id_grid_area()
        # Standard widget styling through CSS: https://stackoverflow.com/questions/507138/how-to-add-a-class-to-a-given-element
        self._classlist = []
        self._elem.classList.add(self.__class__.__name__)
        self._elem.classList.add("ui")
        # Properties
        self._visible = True
        self._render_visible()
        self._color = ""
        self._render_color()
        self._bg_color = ""
        self._render_bg_color()
        self._width = None
        self._render_width()
        self._height = None
        self._render_height()
        self._min_width = None
        self._render_min_width()
        self._min_height = None
        self._render_min_height()
        self._max_width = None
        self._render_max_width()
        self._max_height = None
        self._render_max_height()

    def _insert_id_grid_area(self):
        """Insert state for id and grid area"""
        self._elem.id = self._widget_id
        self._elem.style.gridArea = self._widget_id

    def get_parent(self) -> Self | None:
        """Reference to the parent widget"""
        return self._parent

    def find_id(self, widget_id: str) -> Self | None:
        """Find a reference to the widget with this id"""
        if self._widget_id == widget_id:
            return self
        return None

    def backup_state(self):
        """Override this method to backup runtime DOM state to widget instance fields before pickling to session storage"""
        self._classlist = self._elem.getAttribute("class")

    def _delete_state(self, state: dict[str, Any]):
        """Override this method to delete state keys that cannot be pickled"""
        # Parent could be None for the main widget, parent will be set when the widget is added as child to another widget
        if "_parent" in state.keys():
            del state["_parent"]
        # TypeError: cannot pickle 'pyodide.ffi.JsProxy' object
        # See: https://stackoverflow.com/questions/2345944/exclude-objects-field-from-pickling-in-python
        del state["_elem"]

    def __getstate__(self) -> dict[str, Any]:
        """Magic method to get the object state when pickling"""
        state = self.__dict__.copy()
        self._delete_state(state)
        return state

    def _insert_state(self):
        """Override this method to insert state, for keys that could not be pickled"""
        self._elem = document.createElement(self._tag)
        self._insert_id_grid_area()

    def __setstate__(self, state: dict[str, Any]):
        """Magic method to set the object state when unpickling"""
        self.__dict__.update(state)
        self._insert_state()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        _ensure_unique_id_beyond(self._widget_id)
        self._elem.setAttribute("class", self._classlist)
        # Properties
        self._render_visible()
        self._render_color()
        self._render_bg_color()
        self._render_width()
        self._render_height()
        self._render_min_width()
        self._render_min_height()
        self._render_max_width()
        self._render_max_height()

    def after_page_load(self):
        """Override this method tot execute code after the page DOM has loaded"""

    # Property: dark_mode
    def is_dark_mode(self) -> bool:
        """Accessor"""
        return "inverted" in self._elem.classList

    def set_dark_mode(self, dark_mode: bool) -> Self:
        """Mutator"""
        # See: https://herculino.com/en/blog/semantic_ui_darkmode_part1.html
        if dark_mode:
            if not self.is_dark_mode():
                self._elem.classList.add("inverted")
        else:
            if self.is_dark_mode():
                self._elem.classList.remove("inverted")
        return self

    # Property: visible
    def _render_visible(self):
        """Renderer"""
        self._elem.style.visibility = "inherit" if self._visible else "hidden"

    def is_visible(self) -> bool:
        """Accessor"""
        return self._visible

    def set_visible(self, visible: bool) -> Self:
        """Mutator"""
        if self._visible != visible:
            self._visible = visible
            self._render_visible()
        return self

    # Property: color
    def _render_color(self):
        """Renderer"""
        self._elem.style.color = self._color if self._color != "" else None

    def get_color(self) -> str:
        """Accessor"""
        return self._color

    def set_color(self, color: str) -> Self:
        """Mutator"""
        if self._color != color:
            self._color = color
            self._render_color()
        return self

    # Property: bg_color
    def _render_bg_color(self):
        """Renderer"""
        self._elem.style.backgroundColor = self._bg_color if self._bg_color != "" else None

    def get_bg_color(self) -> str:
        """Accessor"""
        return self._bg_color

    def set_bg_color(self, bg_color: str) -> Self:
        """Mutator"""
        if self._bg_color != bg_color:
            self._bg_color = bg_color
            self._render_bg_color()
        return self

    # Property: width
    def _render_width(self):
        """Renderer"""
        if self._width is not None:
            try:
                pixels = int(self._width)
                self._elem.style.width = str(pixels) + "px"
            except ValueError:
                self._elem.style.width = str(self._width)  # It was not an integer value

    def get_width(self) -> int | str | None:
        """Accessor"""
        return self._width

    def set_width(self, width: int | str | None) -> Self:
        """Mutator"""
        if self._width != width:
            self._width = width
            self._render_width()
        return self

    # Property: height
    def _render_height(self):
        """Renderer"""
        if self._height is not None:
            try:
                pixels = int(self._height)
                self._elem.style.height = str(pixels) + "px"
            except ValueError:
                self._elem.style.height = str(self._height)  # It was not an integer value

    def get_height(self) -> int | str | None:
        """Accessor"""
        return self._height

    def set_height(self, height: int | str | None) -> Self:
        """Mutator"""
        if self._height != height:
            self._height = height
            self._render_height()
        return self

    # Property: min_width
    def _render_min_width(self):
        """Renderer"""
        if self._min_width is not None:
            try:
                pixels = int(self._min_width)
                self._elem.style.minWidth = str(pixels) + "px"
            except ValueError:
                self._elem.style.minWidth = str(self._min_width)  # It was not an integer value

    def get_min_width(self) -> int | str | None:
        """Accessor"""
        return self._min_width

    def set_min_width(self, min_width: int | str | None) -> Self:
        """Mutator"""
        if self._min_width != min_width:
            self._min_width = min_width
            self._render_min_width()
        return self

    # Property: min_height
    def _render_min_height(self):
        """Renderer"""
        if self._min_height is not None:
            try:
                pixels = int(self._min_height)
                self._elem.style.minHeight = str(pixels) + "px"
            except ValueError:
                self._elem.style.minHeight = str(self._min_height)  # It was not an integer value

    def get_min_height(self) -> int | str | None:
        """Accessor"""
        return self._min_height

    def set_min_height(self, min_height: int | str | None) -> Self:
        """Mutator"""
        if self._min_height != min_height:
            self._min_height = min_height
            self._render_min_height()
        return self

    # Property: max_width
    def _render_max_width(self):
        """Renderer"""
        if self._max_width is not None:
            try:
                pixels = int(self._max_width)
                self._elem.style.maxWidth = str(pixels) + "px"
            except ValueError:
                self._elem.style.maxWidth = str(self._max_width)  # It was not an integer value

    def get_max_width(self) -> int | str | None:
        """Accessor"""
        return self._max_width

    def set_max_width(self, max_width: int | str | None) -> Self:
        """Mutator"""
        if self._max_width != max_width:
            self._max_width = max_width
            self._render_max_width()
        return self

    # Property: max_height
    def _render_max_height(self):
        """Renderer"""
        if self._max_height is not None:
            try:
                pixels = int(self._max_height)
                self._elem.style.maxHeight = str(pixels) + "px"
            except ValueError:
                self._elem.style.maxHeight = str(self._max_height)  # It was not an integer value

    def get_max_height(self) -> int | str | None:
        """Accessor"""
        return self._max_height

    def set_max_height(self, max_height: int | str | None) -> Self:
        """Mutator"""
        if self._max_height != max_height:
            self._max_height = max_height
            self._render_max_height()
        return self
