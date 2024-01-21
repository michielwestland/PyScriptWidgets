import base64
import pickle
from js import console, document, sessionStorage, window # type: ignore
from pyodide.ffi import create_proxy # type: ignore

def debugObject(obj):
    console.debug(repr(obj))
    for attr in dir(obj):
        if not attr.startswith("__"):
            console.debug(attr + " = " + repr(getattr(obj, attr)))

def _serializeWidgetsToBase64(mainWidget):
    mainWidget.backupState()
    return base64.b64encode(pickle.dumps(mainWidget)).decode("utf-8")
    
def _deserializeWidgetsFromBase64(stateData):
    mainWidget = pickle.loads(base64.b64decode(stateData.encode("utf-8")))
    mainWidget.restoreState()
    return mainWidget

_mainWidget = None

def findEventTarget(event):
    return _mainWidget.findId(event.target.id)

_STATE_KEY = "state"

def _window_beforeunload(event):
    state = _serializeWidgetsToBase64(_mainWidget)
    sessionStorage.setItem(_STATE_KEY, state)

def bindToDom(MainWidgetClass, rootElementId): 
    global _mainWidget
    state = sessionStorage.getItem(_STATE_KEY)
    if state == None:
        _mainWidget = MainWidgetClass()
    else:
        _mainWidget = _deserializeWidgetsFromBase64(state)
        console.log("Application state restored from browser session storage")
    document.getElementById(rootElementId).appendChild(_mainWidget._elem)
    window.addEventListener("beforeunload", create_proxy(_window_beforeunload))

# DOM: https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model
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
        self._elem = document.createElement(self._tag)
        self._elem.id = self._id

    def getParent(self):
        return self._parent

    def findId(self, id):
        if self._id == id: 
            return self
        return None

    def backupState(self):
        pass

    def _deleteState(self, state):
        if "_parent" in state.keys(): # Parent could be None for the main widget
            del state["_parent"]
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

class PParentWidget(PWidget): 
    
    def __init__(self, tag):
        super().__init__(tag)
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
        
class PPanel(PParentWidget): 
    #TODO insert / replace / remove individual children
    
    #TODO Html grid layout

    def __init__(self):
        super().__init__("div")

class PLabel(PWidget): 
    
    def __init__(self, text):
        super().__init__("span")
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
        self._text = ""
        self._color = ""
        self._clickHandler = None
        self._clickHandlerProxy = None
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

    def getColor(self):
        return self._color

    def setColor(self, color):
        if color == None:
            color = "black"
        if self._color != color:
            self._color = color
            self._elem.setAttribute("style", f"color: {self._color}")
        return self

    def onClick(self, clickHandler):
        if self._clickHandler != clickHandler:
            if self._clickHandlerProxy != None:
                self._elem.removeEventListener("click", self._clickHandlerProxy)
            self._clickHandler = clickHandler
            self._clickHandlerProxy = create_proxy(self._clickHandler)
            self._elem.addEventListener("click", self._clickHandlerProxy)
        return self

    def _deleteState(self, state):
        super()._deleteState(state)
        # TypeError: cannot pickle 'pyodide.ffi.JsProxy' object
        # See: https://stackoverflow.com/questions/2345944/exclude-objects-field-from-pickling-in-python
        del state["_clickHandlerProxy"]

    def restoreState(self):
        super().restoreState()
        self._elem.replaceChildren(document.createTextNode(self._text))
        self._elem.setAttribute("style", f"color: {self._color}")
        self._clickHandlerProxy = create_proxy(self._clickHandler)
        self._elem.addEventListener("click", self._clickHandlerProxy)

class PEdit(PWidget): 

    def __init__(self, value):
        super().__init__("input")
        self._elem.setAttribute("type", "text")
        self._value = ""
        self._placeholder = ""
        self._width = 0
        self.setValue(value)
    
    def getValue(self):
        return self._elem.value
    
    def setValue(self, value):
        self._elem.value = value
        return self
    
    def getPlaceholder(self):
        return self._placeholder

    def setPlaceholder(self, placeholder):
        if placeholder == None:
            placeholder = ""
        if self._placeholder != placeholder:
            self._placeholder = placeholder
            self._elem.setAttribute("placeholder", self._placeholder)
        return self

    def getWidth(self):
        return self._width

    def setWidth(self, width):
        if width == None:
            width = 100
        if self._width != width:
            self._width = width
            self._elem.setAttribute("style", f"width: {self._width}px")
        #TODO Collect style attributes in separate dictionary, and render in a generic way in the one html style element
        return self

    def backupState(self):
        super().backupState()
        self._value = self._elem.value

    def _insertState(self):
        super()._insertState()
        self._elem.setAttribute("type", "text")

    def restoreState(self):
        super().restoreState()
        self._elem.value = self._value
        self._elem.setAttribute("placeholder", self._placeholder)
        self._elem.setAttribute("style", f"width: {self._width}px")
