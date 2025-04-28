"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


from typing import Self

from widgets.input import PInputWidget


class PTextInput(PInputWidget):
    """Text input widget class"""

    def __init__(self, value: str):
        """Constructor, define input type and class attributes"""
        super().__init__("text", value)
        # Properties
        self._placeholder = ""
        self._render_placeholder()
        self._pattern = ""
        self._render_pattern()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_placeholder()
        self._render_pattern()

    # Type: password
    def is_type_password(self) -> bool:
        """Accessor"""
        return self.get_input_type() == "password"

    def set_type_password(self, type_password: bool) -> Self:
        """Mutator"""
        return self.set_input_type("password" if type_password else "text")

    # Type: email
    def is_type_email(self) -> bool:
        """Accessor"""
        return self.get_input_type() == "email"

    def set_type_email(self, type_email: bool) -> Self:
        """Mutator"""
        return self.set_input_type("email" if type_email else "text")

    # Type: tel
    def is_type_tel(self) -> bool:
        """Accessor"""
        return self.get_input_type() == "tel"

    def set_type_tel(self, type_tel: bool) -> Self:
        """Mutator"""
        return self.set_input_type("tel" if type_tel else "text")

    # Type: url
    def is_type_url(self) -> bool:
        """Accessor"""
        return self.get_input_type() == "url"

    def set_type_url(self, type_url: bool) -> Self:
        """Mutator"""
        return self.set_input_type("url" if type_url else "text")

    # Property: placeholder
    def _render_placeholder(self):
        """Renderer"""
        if len(self._placeholder) > 0:
            self._elem_input.setAttribute("placeholder", self._placeholder)
        else:
            self._elem_input.removeAttribute("placeholder")

    def get_placeholder(self) -> str:
        """Accessor"""
        return self._placeholder

    def set_placeholder(self, placeholder: str) -> Self:
        """Mutator"""
        if self._placeholder != placeholder:
            self._placeholder = placeholder
            self._render_placeholder()
        return self

    # Property: pattern
    def _render_pattern(self):
        """Renderer"""
        if len(self._pattern) > 0:
            self._elem_input.setAttribute("pattern", self._pattern)
        else:
            self._elem_input.removeAttribute("pattern")

    def get_pattern(self) -> str:
        """Accessor"""
        return self._pattern

    def set_pattern(self, pattern: str) -> Self:
        """Mutator"""
        if self._pattern != pattern:
            self._pattern = pattern
            self._render_pattern()
        return self
