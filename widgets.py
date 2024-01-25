import base64
import pickle
from js import console, document, sessionStorage, window # type: ignore
from pyodide.ffi.wrappers import add_event_listener, remove_event_listener # type: ignore

_mainWidget = None

_STATE_KEY = "widget_state"

def debugObject(obj):
    console.debug(repr(obj))
    for attr in dir(obj):
        if not attr.startswith("__"):
            console.debug(attr + " = " + repr(getattr(obj, attr)))

def _serializeWidgetsToBase64(mainWidget):
    mainWidget.backupState()
    # See: https://oren-sifri.medium.com/serializing-a-python-object-into-a-plain-text-string-7411b45d099e
    return base64.b64encode(pickle.dumps(mainWidget)).decode("utf-8")
    
def _deserializeWidgetsFromBase64(stateData):
    mainWidget = pickle.loads(base64.b64decode(stateData.encode("utf-8")))
    mainWidget.restoreState()
    return mainWidget

def findEventTarget(event):
    return _mainWidget.findId(event.target.id)

def findMainWidget():
    return _mainWidget

def _window_beforeunload(event):
    state = _serializeWidgetsToBase64(_mainWidget)
    sessionStorage.setItem(_STATE_KEY, state)

def bindToDom(MainWidgetClass, rootElementId): 
    # What is the impact of this? https://developer.chrome.com/blog/enabling-shared-array-buffer/?utm_source=devtools
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

class PWidget: 
        
    _lastUniqueId = 0

    def _generateUniqueId(self):
        PWidget._lastUniqueId = PWidget._lastUniqueId + 1
        return str(PWidget._lastUniqueId)

    def _ensureUniqueIdBeyond(self, id):
        i = int(id)
        if PWidget._lastUniqueId < i:
            PWidget._lastUniqueId = i

    def __init__(self, tag):
        self._tag = tag
        self._parent = None
        self._id = self._generateUniqueId()
        # DOM manipulation: https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model
        self._elem = document.createElement(self._tag)
        self._elem.id = self._id
        # Standard widget styling through CSS: https://stackoverflow.com/questions/507138/how-to-add-a-class-to-a-given-element
        self._elem.classList.add("PWidget")
        self._elem.classList.add("ui")

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
        self._elem.id = self._id

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._insertState()

    def restoreState(self):
        self._ensureUniqueIdBeyond(self._id)
        self._elem.setAttribute("class", self._classlist)

class PCompoundWidget(PWidget):
    
    def __init__(self, tag):
        super().__init__(tag)
        self._elem.classList.add("PCompoundWidget")
        self._children = []

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

    #TODO Insert / replace / remove individual children by index

    def backupState(self):
        super().backupState()
        for c in self._children:
            c.backupState()
    
    def restoreState(self):
        super().restoreState()
        for c in self._children:
            c.restoreState()
        for c in self._children:
            c._parent = self
            self._elem.appendChild(c._elem)
        
class PPanel(PCompoundWidget): 
    
    #TODO Html grid layout: https://www.w3schools.com/css/css_grid.asp

    def __init__(self, vertical):
        super().__init__("div")
        self._elem.classList.add("PPanel")
        self._vertical = False
        self.setVertical(vertical)

    def isVertical(self):
        return self._vertical
    
    def setVertical(self, vertical):
        if self._vertical != vertical:
            self._vertical = vertical
            self._elem.style.flexDirection = "column" if self._vertical else "row"

    def restoreState(self):
        super().restoreState()
        self._elem.style.flexDirection = "column" if self._vertical else "row"

class PLabel(PWidget): 
    
    def __init__(self, text):
        super().__init__("span")
        self._elem.classList.add("PLabel")
        self._text = ""
        self.setText(text)

    def getText(self):
        return self._text

    def setText(self, text):
        if text == None:
            text = ""
        if self._text != text:
            self._text = text
            self._elem.replaceChildren(document.createTextNode(self._text))
        return self

    def restoreState(self):
        super().restoreState()
        self._elem.replaceChildren(document.createTextNode(self._text))

class PButton(PWidget): 

    def __init__(self, text):
        super().__init__("button")
        self._elem.classList.add("PButton")
        self._elem.classList.add("button")
        self._text = ""
        self._icon = ""
        self._color = ""
        self._clickHandler = None
        self.setText(text)
        self.setIcon("")
        self.setColor("black")

    def getText(self):
        return self._text

    def setText(self, text):
        if text == None:
            text = ""
        if self._text != text:
            self._text = text
            self._elem.replaceChildren() #TODO Put identical code blocks in render<Name> functions.
            if len(self._icon) > 0:
                e = document.createElement("i")
                for c in self._icon.split():
                    e.classList.add(c)
                self._elem.appendChild(e)
            s = " " if len(self._icon) > 0 and len(self._text) > 0 else ""
            if len(s + self._text) > 0:
                self._elem.appendChild(document.createTextNode(s + self._text))
        return self

    def getIcon(self):
        return self._icon

    def setIcon(self, icon):
        if icon == None:
            icon = ""
        if self._icon != icon:
            self._icon = icon
            self._elem.replaceChildren() #TODO Put identical code blocks in render<Name> functions.
            if len(self._icon) > 0:
                e = document.createElement("i")
                for c in self._icon.split():
                    e.classList.add(c)
                self._elem.appendChild(e)
            s = " " if len(self._icon) > 0 and len(self._text) > 0 else ""
            if len(s + self._text) > 0:
                self._elem.appendChild(document.createTextNode(s + self._text))
        return self

    def getColor(self):
        return self._color

    def setColor(self, color):
        if color == None:
            color = "black"
        if self._color != color:
            self._color = color
            self._elem.style.color = self._color
        return self

    def onClick(self, clickHandler):
        if self._clickHandler != clickHandler:
            if self._clickHandler != None:
                remove_event_listener(self._elem, "click", self._clickHandler)
            self._clickHandler = clickHandler
            if self._clickHandler != None:
                add_event_listener(self._elem, "click", self._clickHandler)
        return self

    def restoreState(self):
        super().restoreState()
        self._elem.replaceChildren() #TODO Put identical code blocks in render<Name> functions.
        if len(self._icon) > 0:
            e = document.createElement("i")
            for c in self._icon.split():
                e.classList.add(c)
            self._elem.appendChild(e)
        s = " " if len(self._icon) > 0 and len(self._text) > 0 else ""
        if len(s + self._text) > 0:
            self._elem.appendChild(document.createTextNode(s + self._text))
        self._elem.style.color = self._color
        if self._clickHandler != None:
            add_event_listener(self._elem, "click", self._clickHandler)

class PEdit(PWidget): 

    def __init__(self, value):
        super().__init__("div")
        self._elem.classList.add("PEdit")
        self._elem.classList.add("input")
        self._elem_input = document.createElement("input")
        self._elem_input.setAttribute("type", "text")
        self._elem.appendChild(self._elem_input)
        self._value = ""
        self._placeholder = ""
        self._width = 0
        self.setValue(value)
        self.setPlaceholder("")
        self.setWidth(100)
    
    def getValue(self):
        return self._elem_input.value
    
    def setValue(self, value):
        self._elem_input.value = value
        return self
    
    def getPlaceholder(self):
        return self._placeholder

    def setPlaceholder(self, placeholder):
        if placeholder == None:
            placeholder = ""
        if self._placeholder != placeholder:
            self._placeholder = placeholder
            self._elem_input.setAttribute("placeholder", self._placeholder)
        return self

    def getWidth(self):
        return self._width

    def setWidth(self, width):
        if width == None:
            width = 100
        if self._width != width:
            self._width = width
            # See: https://www.w3schools.com/jsref/prop_html_style.asp / https://www.w3schools.com/jsref/dom_obj_style.asp
            self._elem.style.width = str(self._width) + "px"
        return self

    def backupState(self):
        super().backupState()
        self._value = self._elem_input.value

    def _deleteState(self, state):
        super()._deleteState(state)
        del state["_elem_input"]

    def _insertState(self):
        super()._insertState()
        self._elem_input = document.createElement("input")
        self._elem_input.setAttribute("type", "text")
        self._elem.appendChild(self._elem_input)

    def restoreState(self):
        super().restoreState()
        self._elem_input.value = self._value
        self._elem_input.setAttribute("placeholder", self._placeholder)
        self._elem.style.width = str(self._width) + "px"
