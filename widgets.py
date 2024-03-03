"""PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript."""

import base64
import pickle
import zlib
from js import console, sessionStorage  # type: ignore # pylint: disable=import-error

# Prefer pyscript import over more basic js import for the document and window objects
from pyscript import document, window  # type: ignore # pylint: disable=import-error
from pyodide.ffi.wrappers import add_event_listener, remove_event_listener  # type: ignore # pylint: disable=import-error

# TODO Create a SVG version of the logo.

# TODO Add a resize listener to the browser window object. Onresize eventhandler on main widget.
# See: https://developer.mozilla.org/en-US/docs/Web/API/Window/resize_event

# TODO Add a form widget that wraps labels/inputs with divs for error state and that shows error messages.
# See: https://semantic-ui.com/collections/form.html

# TODO Make a progressive web application (PWA).

# TODO Add a SVG widget and widgets for basic shapes using the DOM tree.

# TODO Use a postgres database in de browser local storage from python.
# See: https://electric-sql.com/

# TODO Add widget border property.

# TODO Add widget background image/linear gradient property: linear-gradient(to bottom right, #F0F8FF, white);

# TODO Add image widget.

# TODO Add hyperlink widget.

# TODO Add component classname as style class for easy identification.

# Private global reference to the root widget
_main_widget = None  # pylint: disable=invalid-name

# Constants
_STATE_KEY = "widget_state"
_ID_PREFIX = "e"
_ID_SUPPLEMENT = "_"
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


def _detect_dark_mode():
    """Detect dark mode in the browser"""
    if window.matchMedia and window.matchMedia("(prefers-color-scheme: dark)").matches:
        _main_widget.set_dark_mode(True)


# Store the widget state
def _window_beforeunload(event):  # pylint: disable=unused-argument
    """Save widget tree state in browser session storage, before unloading the page"""
    state = _serialize_to_base64(_main_widget)
    sessionStorage.setItem(_STATE_KEY, state)


# Create or load the widget state and bind to the browser DOM
def bind_to_dom(MainWidgetClass, root_element_id, debug=False):  # pylint: disable=invalid-name
    """Bind the main widget to the dom, or load the widget tree state from browser session storage if available"""
    # What is the impact of: https://developer.chrome.com/blog/enabling-shared-array-buffer/?utm_source=devtools
    global _main_widget  # pylint: disable=global-statement
    state = sessionStorage.getItem(_STATE_KEY)
    if state is None or debug:
        _main_widget = MainWidgetClass()
    else:
        _main_widget = _deserialize_from_base64(state)
        sessionStorage.removeItem(_STATE_KEY)
        console.log("Application state restored from browser session storage")
    _detect_dark_mode()
    document.getElementById(root_element_id).replaceChildren(
        _main_widget._elem  # pylint: disable=protected-access
    )
    # See: https://jeff.glass/post/pyscript-why-create-proxy/
    add_event_listener(window, "beforeunload", _window_beforeunload)
    _main_widget.after_page_load()


class PWidget:  # pylint: disable=too-many-instance-attributes
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
    def is_dark_mode(self):
        """Accessor"""
        return "inverted" in self._elem.classList

    def set_dark_mode(self, dark_mode):
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
        self._elem.style.color = self._color if self._color != "" else None

    def get_color(self):
        """Accessor"""
        return self._color

    def set_color(self, color):
        """Mutator"""
        if self._color != color:
            self._color = color
            self._render_color()
        return self

    # Property: bg_color
    def _render_bg_color(self):
        """Renderer"""
        self._elem.style.backgroundColor = self._bg_color if self._bg_color != "" else None

    def get_bg_color(self):
        """Accessor"""
        return self._bg_color

    def set_bg_color(self, bg_color):
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

    def get_width(self):
        """Accessor"""
        return self._width

    def set_width(self, width):
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

    def get_height(self):
        """Accessor"""
        return self._height

    def set_height(self, height):
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

    # TODO Also implement padding property, move both properties to widget class.

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
        child.set_dark_mode(
            child.get_parent().is_dark_mode()
        )  # Inherit dark mode property from parent
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

    # Property: dark_mode (overridden)
    def set_dark_mode(self, dark_mode):
        """Mutator"""
        super().set_dark_mode(dark_mode)
        for c in self._children:
            c.set_dark_mode(dark_mode)

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

    def is_vertical(self):
        """Accessor"""
        return self._vertical

    def set_vertical(self, vertical):
        """Mutator"""
        if self._vertical != vertical:
            self._vertical = vertical
            self._render_vertical()
        return self

    # Property: wrap
    def _render_wrap(self):
        """Renderer"""
        self._elem.style.flexWrap = "wrap" if self._wrap else "nowrap"

    def is_wrap(self):
        """Accessor"""
        return self._wrap

    def set_wrap(self, wrap):
        """Mutator"""
        if self._wrap != wrap:
            self._wrap = wrap
            self._render_wrap()
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
        all_perc_px = len(self._columns) > 0
        total_px = 0
        for c in self._columns:
            all_perc_px = all_perc_px and (c.endswith("%") or c.endswith("px"))
            if c.endswith("px"):
                total_px += int(c[:-2])
        if all_perc_px:
            # When there are only 'px' and '%' values, convert percentages to a calculation of the percentage of *remaining* space
            arr = []
            for c in self._columns:
                if c.endswith("%"):
                    perc = int(c[:-1])
                    arr.append("calc(" + c + " - " + str(perc * total_px / 100) + "px)")
                else:
                    arr.append(c)
            self._elem.style.gridTemplateColumns = " ".join(arr)
        else:
            self._elem.style.gridTemplateColumns = " ".join(self._columns)

    def get_columns(self):
        """Accessor"""
        return self._columns

    def set_columns(self, columns):
        """Mutator"""
        for index, value in enumerate(columns):
            try:
                pixels = int(value) # Integer values as a convenience
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
        all_perc_px = len(self._rows) > 0
        total_px = 0
        for r in self._rows:
            all_perc_px = all_perc_px and (r.endswith("%") or r.endswith("px"))
            if r.endswith("px"):
                total_px += int(r[:-2])
        if all_perc_px:
            # When there are only 'px' and '%' values, convert percentages to a calculation of the percentage of *remaining* space
            arr = []
            for r in self._rows:
                if r.endswith("%"):
                    perc = int(r[:-1])
                    arr.append("calc(" + r + " - " + str(perc * total_px / 100) + "px)")
                else:
                    arr.append(r)
            self._elem.style.gridTemplateRows = " ".join(arr)
        else:
            self._elem.style.gridTemplateRows = " ".join(self._rows)

    def get_rows(self):
        """Accessor"""
        return self._rows

    def set_rows(self, rows):
        """Mutator"""
        for index, value in enumerate(rows):
            try:
                pixels = int(value) # Integer values as a convenience
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

    def add_child(self, child):
        """Add a single child"""
        if isinstance(child, PCompoundWidget):
            # TODO _BUSY Add overflow scrollbar option to some or all compound widgets.
            child._elem.style.overflow = "auto"  # pylint: disable=protected-access
            child.set_max_width("100%")
            child.set_max_height("100%")
        return super().add_child(child)


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


class PInputWidget(PFocussableWidget):
    """Abstract input widget class with value and shared functionality"""

    def __init__(self, input_type, value):
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
        self._elem_input.id = self._widget_id + _ID_SUPPLEMENT + "input"
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
    def get_value(self):
        """Accessor"""
        return self._elem_input.value

    def set_value(self, value):
        """Mutator"""
        if self._elem_input.value != value:
            self._elem_input.value = value
        return self

    # Property: input_type
    def _render_input_type(self):
        """Renderer"""
        self._elem_input.setAttribute("type", self._input_type)

    def get_input_type(self):
        """Accessor"""
        return self._input_type

    def set_input_type(self, input_type):
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

    # Type: password
    def is_type_password(self):
        """Accessor"""
        return self.get_input_type() == "password"

    def set_type_password(self, type_password):
        """Mutator"""
        return self.set_input_type("password" if type_password else "text")

    # Type: email
    def is_type_email(self):
        """Accessor"""
        return self.get_input_type() == "email"

    def set_type_email(self, type_email):
        """Mutator"""
        return self.set_input_type("email" if type_email else "text")

    # Type: tel
    def is_type_tel(self):
        """Accessor"""
        return self.get_input_type() == "tel"

    def set_type_tel(self, type_tel):
        """Mutator"""
        return self.set_input_type("tel" if type_tel else "text")

    # Type: url
    def is_type_url(self):
        """Accessor"""
        return self.get_input_type() == "url"

    def set_type_url(self, type_url):
        """Mutator"""
        return self.set_input_type("url" if type_url else "text")

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
    """Number input widget class"""

    # TODO Implement number input, format value, properties: min, max, step and decimals


class PDateInput(PInputWidget):
    """Date input widget class"""

    # TODO Implement date input, format value, input types: date, time, datetime-local


class PCheckBox(PInputWidget):
    """Checkbox widget class"""

    # TODO Implement checkbox, see: https://semantic-ui.com/modules/checkbox.html


class PRadioGroup(PCompoundWidget):
    """Radio group widget class"""

    # TODO Implement radio group, see: https://semantic-ui.com/modules/checkbox.html#radio


class PComboBox(PCompoundWidget):
    """Combobox widget class"""

    # TODO Implement combo box, see: https://semantic-ui.com/modules/dropdown.html


class PMenuItem(PWidget):
    """Menu item widget class"""

    # TODO Implement menu item, see: https://semantic-ui.com/collections/menu.html


class PMenu(PCompoundWidget):
    """Menu widget class"""

    # TODO Implement menu, see: https://semantic-ui.com/collections/menu.html#menu


class PMenuBar(PCompoundWidget):
    """Menu bar widget class"""

    # TODO Implement menu bar, see: https://semantic-ui.com/collections/menu.html#sub-menu


class PTable(PCompoundWidget):
    """Table widget class"""

    # TODO Implement table, see: https://semantic-ui.com/collections/table.html


class PTabPane(PCompoundWidget):
    """Tab pane widget class"""

    # TODO Implement tab pane, see: https://semantic-ui.com/modules/tab.html


class PTextArea(PFocussableWidget):
    """Text area widget class"""

    # TODO Implement text area.


class PModal(PCompoundWidget):
    """Modal dialog widget class"""

    # TODO Implement modal widget, see: https://semantic-ui.com/modules/modal.html
