import base64
import pickle
from js import console, sessionStorage # type: ignore
# Prefer pyscript import over more basic js import for the document and window objects
from pyscript import document, window # type: ignore
from pyodide.ffi.wrappers import add_event_listener, remove_event_listener # type: ignore

#TODO Create a SVG version of the logo. 

#TODO Add a resize listener to the browser window object. Onresize eventhandler on main widget. See: https://developer.mozilla.org/en-US/docs/Web/API/Window/resize_event

#TODO Add a form widget that wraps labels/inputs with divs for error state and that shows error messages: https://semantic-ui.com/collections/form.html

#TODO Make a progressive web application (PWA).

# Private global reference to the root widget
_mainWidget = None

# Constants
_STATE_KEY = "widget_state"
_ID_PREFIX = "e"
_ID_SUPPLEMENT = "."
_UTF_8 = "utf-8"

# Debug utiliies
def debugObject(obj):
    """Print object attributes to the debug console"""
    console.debug(repr(obj))
    for attr in dir(obj):
        if not attr.startswith("__"):
            console.debug(attr + " = " + repr(getattr(obj, attr)))

# Global subroutines for (de)serializing the widget tree, when the page (un)loads
def _serializeWidgetsToBase64(mainWidget):
    """Pickle the widget tree and encode binary data as base64"""
    mainWidget.backupState()
    # See: https://oren-sifri.medium.com/serializing-a-python-object-into-a-plain-text-string-7411b45d099e
    return base64.b64encode(pickle.dumps(mainWidget)).decode(_UTF_8)

def _deserializeWidgetsFromBase64(stateData):
    """Decode binary data from base64 and unpickle the widget tree"""
    #TODO Add a hash-signature to the stored data, and verify on load. Encrypt/decrypt and compress/uncompress the stored binary data. 
    mainWidget = pickle.loads(base64.b64decode(stateData.encode(_UTF_8)))
    mainWidget.restoreState()
    return mainWidget

# Global functions to get references to widgets in event handlers
def findEventTarget(event):
    """Find the target widget for this event in the widget tree"""
    id = event.target.id
    i = id.find(_ID_SUPPLEMENT)
    if i >= 0: # Remove id supplement
        id = id[:i]
    return _mainWidget.findId(id)

def findMainWidget():
    """Find the main widget, the root of the widget tree"""
    return _mainWidget

# Store the widget state
def _window_beforeunload(event):
    """Save widget tree state in browser session storage, before unloading the page"""
    state = _serializeWidgetsToBase64(_mainWidget)
    sessionStorage.setItem(_STATE_KEY, state)

# Create or load the widget state and bind to the browser DOM
def bindToDom(MainWidgetClass, rootElementId): 
    """Bind the main widget to the dom, or load the widget tree state from browser session storage if available"""
    # What is the impact of: https://developer.chrome.com/blog/enabling-shared-array-buffer/?utm_source=devtools
    global _mainWidget
    state = sessionStorage.getItem(_STATE_KEY)
    if state is None:
        _mainWidget = MainWidgetClass()
    else:
        _mainWidget = _deserializeWidgetsFromBase64(state)
        sessionStorage.removeItem(_STATE_KEY)
        console.log("Application state restored from browser session storage")
    document.getElementById(rootElementId).replaceChildren(_mainWidget._elem)
    # See: https://jeff.glass/post/pyscript-why-create-proxy/
    add_event_listener(window, "beforeunload", _window_beforeunload)
    _mainWidget.afterPageLoad()

class PWidget: 
    """Abstract widget base class"""
        
    _lastUniqueId = 0

    def _generateUniqueId(self):
        """Generate a new unique widget id, a sequential number"""
        PWidget._lastUniqueId = PWidget._lastUniqueId + 1
        return _ID_PREFIX + str(PWidget._lastUniqueId)

    def _ensureUniqueIdBeyond(self, id):
        """Ensure any new unique widget id, sequential number is beyond the given number"""
        i = int(id[len(_ID_PREFIX):])
        if PWidget._lastUniqueId < i:
            PWidget._lastUniqueId = i

    def __init__(self, tag):
        """Constructor, define tag and class attributes"""
        self._tag = tag
        self._parent = None
        self._id = self._generateUniqueId()
        # DOM manipulation: https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model
        self._elem = document.createElement(self._tag)
        self._insertIdGridArea()
        # Standard widget styling through CSS: https://stackoverflow.com/questions/507138/how-to-add-a-class-to-a-given-element
        self._elem.classList.add("ui")
        # Properties
        self._visible = True
        self._renderVisible()
        self._color = "inherit"
        self._renderColor()

    def _insertIdGridArea(self):
        self._elem.id = self._id
        self._elem.style.gridArea = self._id

    def getParent(self):
        """Reference to the parent widget"""
        return self._parent

    def findId(self, id):
        """Find a reference to the widget with this id"""
        if self._id == id: 
            return self
        return None

    def backupState(self):
        """Override this method to backup runtime DOM state to widget instance fields before pickling to session storage"""
        self._classlist = self._elem.getAttribute("class")

    def _deleteState(self, state):
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
        self._deleteState(state)
        return state

    def _insertState(self):
        """Override this method to insert state, for keys that could not be pickled"""
        self._elem = document.createElement(self._tag)
        self._insertIdGridArea()

    def __setstate__(self, state):
        """Magic method to set the object state when unpickling"""
        self.__dict__.update(state)
        self._insertState()

    def restoreState(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        self._ensureUniqueIdBeyond(self._id)
        self._elem.setAttribute("class", self._classlist)
        # Properties
        self._renderColor()

    def afterPageLoad(self):
        """Override this method tot execute code after the page DOM has loaded"""
        pass

    # Property: Visible
    def _renderVisible(self):
        self._elem.style.visibility = "inherit" if self._visible else "hidden"

    def isVisible(self):
        return self._visible

    def setVisible(self, visible):
        if self._visible != visible:
            self._visible = visible
            self._renderVisible()
        return self

    # Property: Color
    def _renderColor(self):
        self._elem.style.color = self._color

    def getColor(self):
        return self._color

    def setColor(self, color):
        if self._color != color:
            self._color = color
            self._renderColor()
        return self

class PCompoundWidget(PWidget):
    """Abstract compound widget base class, that can have children"""

    def __init__(self, tag):
        """Constructor, define tag and class attributes"""
        super().__init__(tag)
        # Children
        self._children = []
        # Properties
        self._margin = 0
        self._renderMargin()
        self._gap = 0
        self._renderGap()

    def findId(self, id):
        """Find a reference to the widget with this id, also search in children"""
        if self._id == id: 
            return self
        for c in self._children:
            f = c.findId(id)
            if f is not None:
                return f
        return None

    # Children
    def getChildren(self):
        return self._children

    def removeChild(self, child):
        child._parent = None
        self._elem.removeChild(child._elem)
        self._children.remove(child)
        return self

    def removeAllChildren(self):
        self._elem.replaceChildren()
        for c in self._children:
            c._parent = None
        self._children.clear()
        return self

    def addChild(self, child):
        child._parent = self
        self._elem.appendChild(child._elem)
        self._children.append(child)
        return self

    def addChildren(self, children):
        for c in children:
            self.addChild(c)
        return self

    def backupState(self):
        """Override this method to backup runtime DOM state to widget instance fields before pickling to session storage"""
        super().backupState()
        for c in self._children:
            c.backupState()
    
    def restoreState(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restoreState()
        for c in self._children:
            c.restoreState()
            c._parent = self
            self._elem.appendChild(c._elem)
        # Properties
        self._renderGap()
        self._renderMargin()
    
    def afterPageLoad(self):
        super().afterPageLoad()
        for c in self._children:
            c.afterPageLoad()

    # Property: Margin
    def _renderMargin(self):
        self._elem.style.margin = str(self._margin) + "px"

    def getMargin(self):
        return self._margin
    
    def setMargin(self, margin):
        if self._margin != margin:
            self._margin = margin
            self._renderMargin()
        return self

    # Property: Gap
    def _renderGap(self):
        self._elem.style.gap = str(self._gap) + "px"

    def getGap(self):
        return self._gap
    
    def setGap(self, gap):
        if self._gap != gap:
            self._gap = gap
            self._renderGap()
        return self

class PPanel(PCompoundWidget): 
    """Panel widget class with flex layout"""
    
    def __init__(self, vertical):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        # Properties
        self._vertical = vertical
        self._renderVertical()

    def restoreState(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restoreState()
        # Properties
        self._renderVertical()

    # Property: Vertical
    def _renderVertical(self):
        # See: https://flexbox.malven.co
        self._elem.style.display = "flex"
        self._elem.style.alignItems = "baseline"
        self._elem.style.flexWrap = "wrap"
        self._elem.style.flexDirection = "column" if self._vertical else "row"

    def isVertical(self):
        return self._vertical
    
    def setVertical(self, vertical):
        if self._vertical != vertical:
            self._vertical = vertical
            self._renderVertical()
        return self

class PGrid(PCompoundWidget): 
    """Grid widget class with grid layout obviously"""
    
    def __init__(self):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        self._renderDisplay()
        # Properties
        self._columns = []
        self._renderColumns()
        self._rows = []
        self._renderRows()
        self._areas = ""
        self._renderAreas()

    def restoreState(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restoreState()
        self._renderDisplay()
        # Properties
        self._renderColumns()
        self._renderRows()
        self._renderAreas()

    def _renderDisplay(self):
        # See: https://grid.malven.co
        self._elem.style.display = "grid"
        self._elem.style.alignItems = "baseline"

    # Property: Columns
    def _renderColumns(self):
        self._elem.style.gridTemplateColumns = " ".join(self._columns)

    def getColumns(self):
        return self._columns
    
    def setColumns(self, columns):
        for index, value in enumerate(columns):
            try:
                pixels = int(value)
                columns[index] = str(pixels) + "px"
            except ValueError:
                pass # It was not an integer value
        
        if self._columns != columns:
            self._columns = columns
            self._renderColumns()
        return self

    # Property: Rows
    def _renderRows(self):
        self._elem.style.gridTemplateRows = " ".join(self._rows)

    def getRows(self):
        return self._rows
    
    def setRows(self, rows):
        for index, value in enumerate(rows):
            try:
                pixels = int(value)
                rows[index] = str(pixels) + "px"
            except ValueError:
                pass # It was not an integer value
        
        if self._rows != rows:
            self._rows = rows
            self._renderRows()
        return self

    # Property: Areas (readonly)
    def _renderAreas(self):
        self._elem.style.gridTemplateAreas = self._areas

    def setAreas(self, areas):
        #See: https://www.w3schools.com/css/css_grid.asp
        #See: https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas
        self.removeAllChildren()
        
        self._areas = ""
        for line in areas:
            
            areaRow = ""
            for c in line:
                if c is None:
                    areaRow += " ."
                else:
                    if not (c in self.getChildren()):
                        self.addChild(c)
                    areaRow += " " + c._id
            
            if len(areaRow) > 0:
                areaRow = areaRow[1:]
            self._areas += " " + "\"" + areaRow + "\""

        if len(self._areas) > 0:
            self._areas = self._areas[1:]
        self._renderAreas()

class PFocussableWidget(PWidget):
    """Abstract focussable widget class"""
    
    def requestFocus(self):
        #self._elem.scrollIntoView()
        #self._elem.focus()
        elem = document.getElementById(self._id)
        elem.scrollIntoView()
        elem.focus() #TODO _BUSY does not work, maybe add timeout delay: https://stackoverflow.com/questions/17500704/how-can-i-set-focus-on-an-element-in-an-html-form-using-javascript

class PLabel(PFocussableWidget): 
    """Label widget class"""
    
    def __init__(self, text):
        """Constructor, define tag and class attributes"""
        super().__init__("label")
        # Properties
        self._text = text
        self._renderText()
        self._for = None
        self._renderFor()

    def restoreState(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restoreState()
        # Properties
        self._renderText()
        self._renderFor()

    # Property: Text
    def _renderText(self):
        self._elem.replaceChildren(document.createTextNode(self._text))

    def getText(self):
        return self._text

    def setText(self, text):
        if self._text != text:
            self._text = text
            self._renderText()
        return self

    # Property: For
    def _renderFor(self):
        if self._for is None:
            self._elem.removeAttribute("for")
        else:
            self._elem.htmlFor = self._for._id

    def getFor(self):
        return self._for

    def setFor(self, forWidget):
        if id(self._for) != id(forWidget): # Object reference/id comparison
            self._for = forWidget
            self._renderFor()
        return self

class PButton(PFocussableWidget): 
    """Button widget class"""
    
    #See: https://semantic-ui.com/kitchen-sink.html
    def __init__(self, text):
        """Constructor, define tag and class attributes"""
        super().__init__("button")
        self._elem.classList.add("button")
        # Properties
        self._text = text
        self._icon = ""
        self._renderTextIcon()
        self._click = None
        self._renderClick()

    def restoreState(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restoreState()
        # Properties
        self._renderTextIcon()
        self._renderClick()

    # Property: Text
    def _renderTextIcon(self):
        self._elem.replaceChildren()
        if len(self._icon) > 0:
            e = document.createElement("i")
            e.id = self._id + _ID_SUPPLEMENT + "i"
            for c in self._icon.split():
                e.classList.add(c)
            e.classList.add("icon")
            self._elem.appendChild(e)
        s = " " if len(self._icon) > 0 and len(self._text) > 0 else ""
        if len(s + self._text) > 0:
            self._elem.appendChild(document.createTextNode(s + self._text))

    def getText(self):
        return self._text

    def setText(self, text):
        if self._text != text:
            self._text = text
            self._renderTextIcon()
        return self

    # Property: Icon
    def getIcon(self):
        return self._icon

    def setIcon(self, icon):
        if self._icon != icon:
            self._icon = icon
            self._renderTextIcon()
        return self

    # Property: Click
    def _renderClick(self):
        if self._click is not None:
            add_event_listener(self._elem, "click", self._click)

    def onClick(self, click):
        if id(self._click) != id(click): # Object reference/id comparison
            if self._click is not None:
                remove_event_listener(self._elem, "click", self._click)
            self._click = click
            self._renderClick()
        return self

class PInputWidget(PFocussableWidget):
    """Abstract input widget class with value and shared functionality"""

    def __init__(self, type, value):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        self._elem.classList.add("input")
        self._type = type
        self._insertInput()
        # Value
        self.setValue(value)
        # Properties
        self._required = ""
        self._renderRequired()
        self._readonly = False
        self._renderReadonly()
        self._change = None
        self._renderChange()

    def backupState(self):
        """Override this method to backup runtime DOM state to widget instance fields before pickling to session storage"""
        super().backupState()
        self._value = self._elem_input.value

    def _deleteState(self, state):
        """Override this method to delete state keys that cannot be pickled"""
        super()._deleteState(state)
        del state["_elem_input"]

    def _insertInput(self):
        self._elem_input = document.createElement("input")
        self._elem_input.id = self._id + _ID_SUPPLEMENT + "input"
        self._elem_input.setAttribute("type", self._type)
        self._elem.appendChild(self._elem_input)

    def _insertState(self):
        """Override this method to insert state, for keys that could not be pickled"""
        super()._insertState()
        self._insertInput()
    
    def restoreState(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restoreState()
        # Value
        self.setValue(self._value)
        # Properties
        self._renderRequired()
        self._renderReadonly()
        self._renderChange()

    # Value
    def getValue(self):
        return self._elem_input.value
    
    def setValue(self, value):
        if self._elem_input.value != value:
            self._elem_input.value = value
        return self
    
    # Property: Required
    def _renderRequired(self):
        if self._required: 
            self._elem_input.setAttribute("required", "")
        else:
            self._elem_input.removeAttribute("required")

    def getRequired(self):
        return self._required

    def setRequired(self, required):
        if self._required != required:
            self._required = required
            self._renderRequired()
        return self

    # Property: Readonly
    def _renderReadonly(self):
        if self._readonly: 
            self._elem_input.setAttribute("readonly", "")
        else:
            self._elem_input.removeAttribute("readonly")

    def getReadonly(self):
        return self._readonly

    def setReadonly(self, readonly):
        if self._readonly != readonly:
            self._readonly = readonly
            self._renderReadonly()
        return self

    # Property: Change
    def _renderChange(self):
        if self._change is not None:
            add_event_listener(self._elem, "change", self._change)

    def onChange(self, change):
        if id(self._change) != id(change): # Object reference/id comparison
            if self._change is not None:
                remove_event_listener(self._elem, "change", self._change)
            self._change = change
            self._renderChange()
        return self

class PTextInput(PInputWidget): 
    """Text input widget class"""

    def __init__(self, value):
        """Constructor, define input type and class attributes"""
        super().__init__("text", value)
        # Properties
        self._placeholder = ""
        self._renderPlaceholder()
        self._pattern = ""
        self._renderPattern()

    def restoreState(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restoreState()
        # Properties
        self._renderPlaceholder()
        self._renderPattern()

    # Property: Placeholder
    def _renderPlaceholder(self):
        if len(self._placeholder) > 0:
            self._elem_input.setAttribute("placeholder", self._placeholder)
        else:
            self._elem_input.removeAttribute("placeholder")

    def getPlaceholder(self):
        return self._placeholder

    def setPlaceholder(self, placeholder):
        if self._placeholder != placeholder:
            self._placeholder = placeholder
            self._renderPlaceholder()
        return self

    # Property: Pattern
    def _renderPattern(self):
        if len(self._pattern) > 0:
            self._elem_input.setAttribute("pattern", self._pattern)
        else:
            self._elem_input.removeAttribute("pattern")

    def getPattern(self):
        return self._pattern

    def setPattern(self, pattern):
        if self._pattern != pattern:
            self._pattern = pattern
            self._renderPattern()
        return self

class PNumberInput(PInputWidget):
    #TODO Implement number widget class
    pass

class PDateInput(PInputWidget):
    #TODO Implement date widget class
    pass

class PCheckBox(PInputWidget):
    #TODO Implement checkbox widget class, see: https://semantic-ui.com/modules/checkbox.html
    pass

class PRadioGroup(PCompoundWidget):
    #TODO Implement radiogroup widget class, see: https://semantic-ui.com/modules/checkbox.html#radio 
    pass

class PComboBox(PCompoundWidget):
    #TODO Implement combobox widget class, see: https://semantic-ui.com/modules/dropdown.html
    pass

class PMenuitem(PWidget):
    #TODO Implement menu item widget class, see: https://semantic-ui.com/collections/menu.html
    pass

class PMenu(PCompoundWidget):
    #TODO Implement menu widget class, see: https://semantic-ui.com/collections/menu.html#menu
    pass

class PMenuBar(PCompoundWidget):
    #TODO Implement menu bar widget class, see: https://semantic-ui.com/collections/menu.html#sub-menu 
    pass

class PTable(PCompoundWidget):
    #TODO Implement table widget class, see: https://semantic-ui.com/collections/table.html 
    pass

class PTabPane(PCompoundWidget):
    #TODO Implement tab pane widget class, see: https://semantic-ui.com/modules/tab.html 
    pass

class PTextArea(PFocussableWidget):
    #TODO Implement text area widget class 
    pass

class PModal(PCompoundWidget):
    #TODO Implement modal widget class, see: https://semantic-ui.com/modules/modal.html
    pass
