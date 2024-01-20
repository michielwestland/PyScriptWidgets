import uuid
from js import document # type: ignore
from pyodide.ffi import create_proxy # type: ignore

# DOM documentation:
# https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model

class PWidget: 
    
    def __init__(self, tag):
        self._tag = tag
        self._parent = None
        self._id = str(uuid.uuid4()) #TODO Find a more memory efficient algorithm
        self._elem = document.createElement(self._tag)
        self._elem.id = self._id

    def getParent(self):
        return self._parent

    def findId(self, id):
        if self._id == id: 
            return self
        return None
    
    def findTarget(self, event):
        return self.findId(event.target.id)

    def backupState(self):
        pass

    def _deleteState(self, state):
        if "_parent" in state.keys(): # Could be None for the root (app) widget
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
        pass

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

    def __init__(self, rootElementId: str = None):
        super().__init__("div")
        self._rootElementId = rootElementId
        if self._rootElementId != None:
            document.getElementById(self._rootElementId).appendChild(self._elem)

    def restoreState(self):
        super().restoreState()
        if self._rootElementId != None:
            document.getElementById(self._rootElementId).appendChild(self._elem)

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
