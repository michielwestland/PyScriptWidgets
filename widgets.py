"""PyScript widgets"""

import base64
import pickle
import zlib
from js import console, sessionStorage  # type: ignore # pylint: disable=import-error

# Prefer pyscript import over more basic js import for the document and window objects
from pyscript import document, window  # type: ignore # pylint: disable=import-error
from pyodide.ffi.wrappers import add_event_listener, remove_event_listener  # type: ignore # pylint: disable=import-error

# TODO Add light/dark theme.
# See: https://semantic-ui.com/usage/theming.html
# See: http://learnsemantic.com/themes/overview.html
# See: https://github.com/Semantic-Org/Semantic-UI/blob/master/semantic.json.example
# See: https://github.com/Semantic-Org/example-github/blob/master/semantic/src/theme.config

# TODO Create a SVG version of the logo.

# TODO Add a resize listener to the browser window object. Onresize eventhandler on main widget. See: https://developer.mozilla.org/en-US/docs/Web/API/Window/resize_event

# TODO Add a form widget that wraps labels/inputs with divs for error state and that shows error messages: https://semantic-ui.com/collections/form.html

# TODO Make a progressive web application (PWA).

# TODO Add a SVG widget and widgets for basic shapes using the DOM tree.

# Private global reference to the root widget
_main_widget = None  # pylint: disable=invalid-name

# Constants
_STATE_KEY = "widget_state"
_ID_PREFIX = "e"
_ID_SUPPLEMENT = "."
_UTF_8 = "utf-8"


# Debug utiliies
def debug_object(obj):
    """Print object attributes to the debug console"""
    console.debug(repr(obj))
    for attr in dir(obj):
        if not attr.startswith("__"):
            console.debug(attr + " = " + repr(getattr(obj, attr)))


# Global subroutines for (de)serializing the widget tree, when the page (un)loads
def _serialize_to_base64(root_widget):
    """Pickle the widget tree and encode binary data as base64"""
    root_widget.backup_state()
    # See: https://oren-sifri.medium.com/serializing-a-python-object-into-a-plain-text-string-7411b45d099e
    return base64.b64encode(zlib.compress(pickle.dumps(root_widget))).decode(_UTF_8)


def _deserialize_from_base64(state_data):
    """Decode binary data from base64 and unpickle the widget tree"""
    root_widget = pickle.loads(zlib.decompress(base64.b64decode(state_data.encode(_UTF_8))))
    root_widget.restore_state()
    return root_widget


# Global functions to get references to widgets in event handlers
def find_event_target(event):
    """Find the target widget for this event in the widget tree"""
    widget_id = event.target.id
    i = widget_id.find(_ID_SUPPLEMENT)
    if i >= 0:  # Remove id supplement
        widget_id = widget_id[:i]
    return _main_widget.findId(widget_id)


def find_main_widget():
    """Find the main widget, the root of the widget tree"""
    return _main_widget


# Store the widget state
def _window_beforeunload(event):  # pylint: disable=unused-argument
    """Save widget tree state in browser session storage, before unloading the page"""
    state = _serialize_to_base64(_main_widget)
    sessionStorage.setItem(_STATE_KEY, state)


# Create or load the widget state and bind to the browser DOM
def bind_to_dom(MainWidgetClass, root_element_id):  # pylint: disable=invalid-name
    """Bind the main widget to the dom, or load the widget tree state from browser session storage if available"""
    # What is the impact of: https://developer.chrome.com/blog/enabling-shared-array-buffer/?utm_source=devtools
    global _main_widget  # pylint: disable=global-statement
    state = sessionStorage.getItem(_STATE_KEY)
    if state is None:
        _main_widget = MainWidgetClass()
    else:
        _main_widget = _deserialize_from_base64(state)
        sessionStorage.removeItem(_STATE_KEY)
        console.log("Application state restored from browser session storage")
    document.getElementById(root_element_id).replaceChildren(
        _main_widget._elem
    )  # pylint: disable=protected-access
    # See: https://jeff.glass/post/pyscript-why-create-proxy/
    add_event_listener(window, "beforeunload", _window_beforeunload)
    _main_widget.after_page_load()


class PWidget:
    """Abstract widget base class"""

    _last_unique_id = 0

    def _generate_unique_id(self):
        """Generate a new unique widget id, a sequential number"""
        PWidget._last_unique_id = PWidget._last_unique_id + 1
        return _ID_PREFIX + str(PWidget._last_unique_id)

    def _ensure_unique_id_beyond(self, widget_id):
        """Ensure any new unique widget id, sequential number is beyond the given number"""
        i = int(widget_id[len(_ID_PREFIX) :])
        PWidget._last_unique_id = max(PWidget._last_unique_id, i)

    def __init__(self, tag):
        """Constructor, define tag and class attributes"""
        self._tag = tag
        self._parent = None
        self._widget_id = self._generate_unique_id()
        # DOM manipulation: https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model
        self._elem = document.createElement(self._tag)
        self._insert_id_grid_area()
        # Standard widget styling through CSS: https://stackoverflow.com/questions/507138/how-to-add-a-class-to-a-given-element
        self._classlist = []
        self._elem.classList.add("ui")
        # Properties
        self._visible = True
        self._render_visible()
        self._color = "inherit"
        self._render_color()
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

    def get_parent(self):
        """Reference to the parent widget"""
        return self._parent

    def find_id(self, widget_id):
        """Find a reference to the widget with this id"""
        if self._widget_id == widget_id:
            return self
        return None

    def backup_state(self):
        """Override this method to backup runtime DOM state to widget instance fields before pickling to session storage"""
        self._classlist = self._elem.getAttribute("class")

    def _delete_state(self, state):
        """Override this method to delete state keys that cannot be pickled"""
        # Parent could be None for the main widget, parent will be set when the widget is added as child to another widget
        if "_parent" in state.keys():
            del state["_parent"]
        # TypeError: cannot pickle 'pyodide.ffi.JsProxy' object
        # See: https://stackoverflow.com/questions/2345944/exclude-objects-field-from-pickling-in-python
        del state["_elem"]

    def __getstate__(self):
        """Magic method to get the object state when pickling"""
        state = self.__dict__.copy()
        self._delete_state(state)
        return state

    def _insert_state(self):
        """Override this method to insert state, for keys that could not be pickled"""
        self._elem = document.createElement(self._tag)
        self._insert_id_grid_area()

    def __setstate__(self, state):
        """Magic method to set the object state when unpickling"""
        self.__dict__.update(state)
        self._insert_state()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        self._ensure_unique_id_beyond(self._widget_id)
        self._elem.setAttribute("class", self._classlist)
        # Properties
        self._render_visible()
        self._render_color()
        self._render_min_width()
        self._render_min_height()
        self._render_max_width()
        self._render_max_height()

    def after_page_load(self):
        """Override this method tot execute code after the page DOM has loaded"""

    # Property: visible
    def _render_visible(self):
        """Renderer"""
        self._elem.style.visibility = "inherit" if self._visible else "hidden"

    def is_visible(self):
        """Accessor"""
        return self._visible

    def set_visible(self, visible):
        """Mutator"""
        if self._visible != visible:
            self._visible = visible
            self._render_visible()
        return self

    # Property: color
    def _render_color(self):
        """Renderer"""
        self._elem.style.color = self._color

    def get_color(self):
        """Accessor"""
        return self._color

    def set_color(self, color):
        """Mutator"""
        if self._color != color:
            self._color = color
            self._render_color()
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

    def get_min_width(self):
        """Accessor"""
        return self._min_width

    def set_min_width(self, min_width):
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

    def get_min_height(self):
        """Accessor"""
        return self._min_height

    def set_min_height(self, min_height):
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

    def get_max_width(self):
        """Accessor"""
        return self._max_width

    def set_max_width(self, max_width):
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

    def get_max_height(self):
        """Accessor"""
        return self._max_height

    def set_max_height(self, max_height):
        """Mutator"""
        if self._max_height != max_height:
            self._max_height = max_height
            self._render_max_height()
        return self


class PCompoundWidget(PWidget):
    """Abstract compound widget base class, that can have children"""

    # TODO Add scrollbar options.

    def __init__(self, tag):
        """Constructor, define tag and class attributes"""
        super().__init__(tag)
        # Children
        self._children = []
        # Properties
        self._margin = 0
        self._render_margin()
        self._gap = 0
        self._render_gap()

    def find_id(self, widget_id):
        """Find a reference to the widget with this id, also search in children"""
        if self._widget_id == widget_id:
            return self
        for c in self._children:
            f = c.findId(widget_id)
            if f is not None:
                return f
        return None

    # Children
    def get_children(self):
        """Get the list of children"""
        return self._children

    def remove_child(self, child):
        """Remove a single child"""
        child._parent = None  # pylint: disable=protected-access
        self._elem.removeChild(child._elem)  # pylint: disable=protected-access
        self._children.remove(child)
        return self

    def remove_all_children(self):
        """Remove all children"""
        self._elem.replaceChildren()
        for c in self._children:
            c._parent = None  # pylint: disable=protected-access
        self._children.clear()
        return self

    def add_child(self, child):
        """Add a single child"""
        child._parent = self  # pylint: disable=protected-access
        self._elem.appendChild(child._elem)  # pylint: disable=protected-access
        self._children.append(child)
        return self

    def add_children(self, children):
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
        self._render_gap()
        self._render_margin()

    def after_page_load(self):
        """Override this method tot execute code after the page DOM has loaded"""
        super().after_page_load()
        for c in self._children:
            c.after_page_load()

    # Property: margin
    def _render_margin(self):
        """Renderer"""
        self._elem.style.margin = str(self._margin) + "px"

    def get_margin(self):
        """Accessor"""
        return self._margin

    def set_margin(self, margin):
        """Mutator"""
        if self._margin != margin:
            self._margin = margin
            self._render_margin()
        return self

    # Property: gap
    def _render_gap(self):
        """Renderer"""
        self._elem.style.gap = str(self._gap) + "px"

    def get_gap(self):
        """Accessor"""
        return self._gap

    def set_gap(self, gap):
        """Mutator"""
        if self._gap != gap:
            self._gap = gap
            self._render_gap()
        return self


class PPanel(PCompoundWidget):
    """Panel widget class with flex layout"""

    def __init__(self, vertical):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        # Properties
        self._vertical = vertical
        self._render_vertical()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_vertical()

    # Property: vertical
    def _render_vertical(self):
        """Renderer"""
        # See: https://flexbox.malven.co
        self._elem.style.display = "flex"
        self._elem.style.alignItems = "baseline"
        self._elem.style.flexWrap = "wrap"
        self._elem.style.flexDirection = "column" if self._vertical else "row"

    def is_vertical(self):
        """Accessor"""
        return self._vertical

    def set_vertical(self, vertical):
        """Mutator"""
        if self._vertical != vertical:
            self._vertical = vertical
            self._render_vertical()
        return self


class PGrid(PCompoundWidget):
    """Grid widget class with grid layout obviously"""

    def __init__(self):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        self._insert_display()
        # Properties
        self._columns = []
        self._render_columns()
        self._rows = []
        self._render_rows()
        self._areas = ""
        self._render_areas()

    def _insert_state(self):
        """Override this method to insert state, for keys that could not be pickled"""
        super()._insert_state()
        self._insert_display()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_columns()
        self._render_rows()
        self._render_areas()

    def _insert_display(self):
        # See: https://grid.malven.co
        self._elem.style.display = "grid"
        self._elem.style.alignItems = "baseline"

    # Property: columns
    def _render_columns(self):
        """Renderer"""
        self._elem.style.gridTemplateColumns = " ".join(self._columns)

    def get_columns(self):
        """Accessor"""
        return self._columns

    def set_columns(self, columns):
        """Mutator"""
        for index, value in enumerate(columns):
            try:
                pixels = int(value)
                columns[index] = str(pixels) + "px"
            except ValueError:
                pass  # It was not an integer value

        if self._columns != columns:
            self._columns = columns
            self._render_columns()
        return self

    # Property: rows
    def _render_rows(self):
        """Renderer"""
        self._elem.style.gridTemplateRows = " ".join(self._rows)

    def get_rows(self):
        """Accessor"""
        return self._rows

    def set_rows(self, rows):
        """Mutator"""
        for index, value in enumerate(rows):
            try:
                pixels = int(value)
                rows[index] = str(pixels) + "px"
            except ValueError:
                pass  # It was not an integer value

        if self._rows != rows:
            self._rows = rows
            self._render_rows()
        return self

    # Property: areas (readonly)
    def _render_areas(self):
        """Renderer"""
        self._elem.style.gridTemplateAreas = self._areas

    def set_areas(self, areas):
        """Mutator"""
        # See: https://www.w3schools.com/css/css_grid.asp
        # See: https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas
        self.remove_all_children()

        self._areas = ""
        for line in areas:

            area_row = ""
            for c in line:
                if c is None:
                    area_row += " ."
                else:
                    if not c in self.get_children():
                        self.add_child(c)
                    area_row += " " + c._widget_id  # pylint: disable=protected-access

            if len(area_row) > 0:
                area_row = area_row[1:]
            self._areas += " " + '"' + area_row + '"'

        if len(self._areas) > 0:
            self._areas = self._areas[1:]
        self._render_areas()


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


class PButton(PFocussableWidget):
    """Button widget class"""

    # See: https://semantic-ui.com/kitchen-sink.html
    def __init__(self, text):
        """Constructor, define tag and class attributes"""
        super().__init__("button")
        self._elem.classList.add("button")
        # Properties
        self._text = text
        self._icon = ""
        self._render_text_con()
        self._click = None
        self._render_click()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_text_con()
        self._render_click()

    # Property: text
    def _render_text_con(self):
        """Renderer"""
        self._elem.replaceChildren()
        if len(self._icon) > 0:
            e = document.createElement("i")
            e.id = self._widget_id + _ID_SUPPLEMENT + "i"
            for c in self._icon.split():
                e.classList.add(c)
            e.classList.add("icon")
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
            self._render_text_con()
        return self

    # Property: icon
    def get_icon(self):
        """Accessor"""
        return self._icon

    def set_icon(self, icon):
        """Mutator"""
        if self._icon != icon:
            self._icon = icon
            self._render_text_con()
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


class PInputWidget(PFocussableWidget):
    """Abstract input widget class with value and shared functionality"""

    def __init__(self, widget_type, value):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        self._elem.classList.add("input")
        self._widget_type = widget_type
        self._insert_input()
        self._render_enabled()
        # Value
        self._value = ""
        self.set_value(value)
        # Properties
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
        self._elem_input = document.createElement("input")
        self._elem_input.id = self._widget_id + _ID_SUPPLEMENT + "input"
        self._elem_input.setAttribute("type", self._widget_type)
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
        self._render_required()
        self._render_readonly()
        self._render_change()

    def request_focus(self):
        self._elem_input.scrollIntoView()
        self._elem_input.focus()

    def _render_enabled(self):
        if hasattr(self, "_elem_input"):
            if self._enabled:
                self._elem_input.removeAttribute("disabled")
            else:
                self._elem_input.setAttribute("disabled", "")

    # Value
    def get_value(self):
        """Accessor"""
        return self._elem_input.value

    def set_value(self, value):
        """Mutator"""
        if self._elem_input.value != value:
            self._elem_input.value = value
        return self

    # Property: required
    def _render_required(self):
        """Renderer"""
        if self._required:
            self._elem_input.setAttribute("required", "")
        else:
            self._elem_input.removeAttribute("required")

    def is_required(self):
        """Accessor"""
        return self._required

    def set_required(self, required):
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

    def is_readonly(self):
        """Accessor"""
        return self._readonly

    def set_readonly(self, readonly):
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

    def on_change(self, change):
        """Mutator"""
        if id(self._change) != id(change):  # Object reference/id comparison
            if self._change is not None:
                remove_event_listener(self._elem, "change", self._change)
            self._change = change
            self._render_change()
        return self


class PTextInput(PInputWidget):
    """Text input widget class"""

    # TODO Add subtype property: text, password, email, tel, url

    def __init__(self, value):
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

    # Property: placeholder
    def _render_placeholder(self):
        """Renderer"""
        if len(self._placeholder) > 0:
            self._elem_input.setAttribute("placeholder", self._placeholder)
        else:
            self._elem_input.removeAttribute("placeholder")

    def get_placeholder(self):
        """Accessor"""
        return self._placeholder

    def set_placeholder(self, placeholder):
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

    def get_pattern(self):
        """Accessor"""
        return self._pattern

    def set_pattern(self, pattern):
        """Mutator"""
        if self._pattern != pattern:
            self._pattern = pattern
            self._render_pattern()
        return self


class PNumberInput(PInputWidget):
    # TODO Implement number widget class; properties: min, max, step and decimals
    pass


class PDateInput(PInputWidget):
    # TODO Implement date widget class; subtypes: date, time, datetime-local
    pass


class PCheckBox(PInputWidget):
    # TODO Implement checkbox widget class, see: https://semantic-ui.com/modules/checkbox.html
    pass


class PRadioGroup(PCompoundWidget):
    # TODO Implement radiogroup widget class, see: https://semantic-ui.com/modules/checkbox.html#radio
    pass


class PComboBox(PCompoundWidget):
    # TODO Implement combobox widget class, see: https://semantic-ui.com/modules/dropdown.html
    pass


class PMenuitem(PWidget):
    # TODO Implement menu item widget class, see: https://semantic-ui.com/collections/menu.html
    pass


class PMenu(PCompoundWidget):
    # TODO Implement menu widget class, see: https://semantic-ui.com/collections/menu.html#menu
    pass


class PMenuBar(PCompoundWidget):
    # TODO Implement menu bar widget class, see: https://semantic-ui.com/collections/menu.html#sub-menu
    pass


class PTable(PCompoundWidget):
    # TODO Implement table widget class, see: https://semantic-ui.com/collections/table.html
    pass


class PTabPane(PCompoundWidget):
    # TODO Implement tab pane widget class, see: https://semantic-ui.com/modules/tab.html
    pass


class PTextArea(PFocussableWidget):
    # TODO Implement text area widget class
    pass


class PModal(PCompoundWidget):
    # TODO Implement modal widget class, see: https://semantic-ui.com/modules/modal.html
    pass
