import base64
import pickle
from js import console, document, sessionStorage, window # type: ignore
from pyodide.ffi.wrappers import add_event_listener, remove_event_listener # type: ignore

# Private global reference to the root widget
_mainWidget = None

# Constants
_STATE_KEY = "widget_state"
_ID_PREFIX = "e"
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
    mainWidget.backupState()
    # See: https://oren-sifri.medium.com/serializing-a-python-object-into-a-plain-text-string-7411b45d099e
    return base64.b64encode(pickle.dumps(mainWidget)).decode(_UTF_8)
    
def _deserializeWidgetsFromBase64(stateData):
    mainWidget = pickle.loads(base64.b64decode(stateData.encode(_UTF_8)))
    mainWidget.restoreState()
    return mainWidget

# Global functions to get references to widgets in event handlers
def findEventTarget(event):
    return _mainWidget.findId(event.target.id)

def findMainWidget():
    return _mainWidget

# Store the widget state
def _window_beforeunload(event):
    state = _serializeWidgetsToBase64(_mainWidget)
    sessionStorage.setItem(_STATE_KEY, state)

# Create or load the widget state and bind to the browser DOM
def bindToDom(MainWidgetClass, rootElementId): 
    # What is the impact of: https://developer.chrome.com/blog/enabling-shared-array-buffer/?utm_source=devtools
    global _mainWidget
    state = sessionStorage.getItem(_STATE_KEY)
    if state == None:
        _mainWidget = MainWidgetClass()
    else:
        _mainWidget = _deserializeWidgetsFromBase64(state)
        console.log("Application state restored from browser session storage")
    document.getElementById(rootElementId).appendChild(_mainWidget._elem)
    # See: https://jeff.glass/post/pyscript-why-create-proxy/
    add_event_listener(window, "beforeunload", _window_beforeunload)
    _mainWidget.afterPageLoad()

class PWidget: 
        
    _lastUniqueId = 0

    def _generateUniqueId(self):
        PWidget._lastUniqueId = PWidget._lastUniqueId + 1
        return _ID_PREFIX + str(PWidget._lastUniqueId)

    def _ensureUniqueIdBeyond(self, id):
        i = int(id[len(_ID_PREFIX):])
        if PWidget._lastUniqueId < i:
            PWidget._lastUniqueId = i

    def __init__(self, tag):
        self._tag = tag
        self._parent = None
        self._id = self._generateUniqueId()
        # DOM manipulation: https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model
        self._elem = document.createElement(self._tag)
        self._renderIdGridArea()
        # Standard widget styling through CSS: https://stackoverflow.com/questions/507138/how-to-add-a-class-to-a-given-element
        self._elem.classList.add("ui")

    def _renderIdGridArea(self):
        self._elem.id = self._id
        self._elem.style.gridArea = self._id

    def getParent(self):
        return self._parent

    def findId(self, id):
        if self._id == id: 
            return self
        return None

    def backupState(self):
        self._classlist = self._elem.getAttribute("class")

    def _deleteState(self, state):
        if "_parent" in state.keys(): # Parent could be None for the main widget
            del state["_parent"]
        # TypeError: cannot pickle 'pyodide.ffi.JsProxy' object
        # See: https://stackoverflow.com/questions/2345944/exclude-objects-field-from-pickling-in-python
        del state["_elem"]

    def __getstate__(self):
        state = self.__dict__.copy()
        self._deleteState(state)
        return state

    def _insertState(self):
        self._elem = document.createElement(self._tag)
        self._renderIdGridArea()

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._insertState()

    def restoreState(self):
        self._ensureUniqueIdBeyond(self._id)
        self._elem.setAttribute("class", self._classlist)

    def afterPageLoad(self):
        pass

class PCompoundWidget(PWidget):
    
    def __init__(self, tag):
        super().__init__(tag)
        self._children = []
        self._gap = 0
        self._renderGap()
        self._margin = 0
        self._renderMargin()

    def findId(self, id):
        if self._id == id: 
            return self
        for c in self._children:
            f = c.findId(id)
            if f != None:
                return f
        return None

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

    def _renderGap(self):
        self._elem.style.gap = str(self._gap) + "px"

    def getGap(self):
        return self._gap
    
    def setGap(self, gap):
        if self._gap != gap:
            self._gap = gap
            self._renderGap()
        return self

    def _renderMargin(self):
        self._elem.style.margin = str(self._margin) + "px"

    def getMargin(self):
        return self._margin
    
    def setMargin(self, margin):
        if self._margin != margin:
            self._margin = margin
            self._renderMargin()
        return self

    def backupState(self):
        super().backupState()
        for c in self._children:
            c.backupState()
    
    def restoreState(self):
        super().restoreState()
        for c in self._children:
            c.restoreState()
            c._parent = self
            self._elem.appendChild(c._elem)
        self._renderGap()
        self._renderMargin()
    
    def afterPageLoad(self):
        super().afterPageLoad()
        for c in self._children:
            c.afterPageLoad()

class PPanel(PCompoundWidget): 
    
    def __init__(self, vertical):
        super().__init__("div")
        self._renderDisplay()
        self._vertical = vertical
        self._renderVertical()

    def _renderDisplay(self):
        # See: https://flexbox.malven.co
        self._elem.style.display = "flex"

    def _renderVertical(self):
        self._elem.style.flexDirection = "column" if self._vertical else "row"

    def isVertical(self):
        return self._vertical
    
    def setVertical(self, vertical):
        if self._vertical != vertical:
            self._vertical = vertical
            self._renderVertical()
        return self

    def restoreState(self):
        super().restoreState()
        self._renderDisplay()
        self._renderVertical()

class PGrid(PCompoundWidget): 
    
    def __init__(self):
        super().__init__("div")
        self._renderDisplay()
        self._columns = []
        self._renderColumns()
        self._rows = []
        self._renderRows()
        self._areas = ""
        self._renderAreas()

    def _renderDisplay(self):
        # See: https://grid.malven.co
        self._elem.style.display = "grid"

    def _renderColumns(self):
        self._elem.style.gridTemplateColumns = " ".join(self._columns)

    def getColumns(self):
        return self._columns
    
    def setColumns(self, columns):
        if self._columns != columns:
            self._columns = columns
            self._renderColumns()
        return self

    def _renderRows(self):
        self._elem.style.gridTemplateRows = " ".join(self._rows)

    def getRows(self):
        return self._rows
    
    def setRows(self, rows):
        if self._rows != rows:
            self._rows = rows
            self._renderRows()
        return self

    def _renderAreas(self):
        self._elem.style.gridTemplateAreas = self._areas

    # Read only property, no getAreas() method
    def setAreas(self, areas):
        #See: https://www.w3schools.com/css/css_grid.asp
        #See: https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas
        self.removeAllChildren()
        
        self._areas = ""
        for line in areas:
            
            areaRow = ""
            for c in line:
                if c == None:
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

    def restoreState(self):
        super().restoreState()
        self._renderDisplay()
        self._renderColumns()
        self._renderRows()
        self._renderAreas()

class PLabel(PWidget): 
    
    def __init__(self, text):
        super().__init__("label")
        self._text = text
        self._renderText()

    def _renderText(self):
        self._elem.replaceChildren(document.createTextNode(self._text))

    def getText(self):
        return self._text

    def setText(self, text):
        if self._text != text:
            self._text = text
            self._renderText()
        return self

    def restoreState(self):
        super().restoreState()
        self._renderText()

class PButton(PWidget): 

    def __init__(self, text):
        super().__init__("button")
        self._elem.classList.add("button")
        self._text = text
        self._icon = ""
        self._renderTextIcon()
        self._color = "black"
        self._renderColor()
        self._clickHandler = None
        self._renderClickHandler()

    def _renderTextIcon(self):
        self._elem.replaceChildren()
        if len(self._icon) > 0:
            e = document.createElement("i")
            for c in self._icon.split():
                e.classList.add(c)
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

    def getIcon(self):
        return self._icon

    def setIcon(self, icon):
        if self._icon != icon:
            self._icon = icon
            self._renderTextIcon()
        return self

    def _renderColor(self):
        self._elem.style.color = self._color

    def getColor(self): #TODO Move to widget class
        return self._color

    def setColor(self, color):
        if self._color != color:
            self._color = color
            self._renderColor()
        return self

    def _renderClickHandler(self):
        if self._clickHandler != None:
            add_event_listener(self._elem, "click", self._clickHandler)

    def onClick(self, clickHandler):
        if self._clickHandler != clickHandler:
            if self._clickHandler != None:
                remove_event_listener(self._elem, "click", self._clickHandler)
            self._clickHandler = clickHandler
            self._renderClickHandler()
        return self

    def restoreState(self):
        super().restoreState()
        self._renderTextIcon()
        self._renderColor()
        self._renderClickHandler()

class PEdit(PWidget): 

    def __init__(self, value):
        super().__init__("div")
        self._elem.classList.add("input")
        self._insertInnerInput()
        self.setValue(value)
        self._placeholder = ""
        self._renderPlaceholder()
        self._width = 100 #TODO Move to widget class, also make height attribute
        self._renderWidth()

    def getValue(self):
        return self._elem_input.value
    
    def setValue(self, value):
        self._elem_input.value = value
        return self
    
    def _renderPlaceholder(self):
        self._elem_input.setAttribute("placeholder", self._placeholder)

    def getPlaceholder(self):
        return self._placeholder

    def setPlaceholder(self, placeholder):
        if self._placeholder != placeholder:
            self._placeholder = placeholder
            self._renderPlaceholder()
        return self

    def _renderWidth(self):
        # See: https://www.w3schools.com/jsref/prop_html_style.asp / https://www.w3schools.com/jsref/dom_obj_style.asp
        self._elem.style.width = str(self._width) + "px"

    def getWidth(self):
        return self._width

    def setWidth(self, width):
        if self._width != width:
            self._width = width
            self._renderWidth()
        return self

    def backupState(self):
        super().backupState()
        self._value = self._elem_input.value

    def _deleteState(self, state):
        super()._deleteState(state)
        del state["_elem_input"]

    def _insertInnerInput(self):
        self._elem_input = document.createElement("input")
        self._elem_input.setAttribute("type", "text")
        self._elem.appendChild(self._elem_input)

    def _insertState(self):
        super()._insertState()
        self._insertInnerInput()
    
    def restoreState(self):
        super().restoreState()
        self._elem_input.value = self._value
        self._renderPlaceholder()
        self._renderWidth()
