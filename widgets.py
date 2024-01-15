from js import document # type: ignore
from pyodide.ffi import create_proxy # type: ignore

# DOM documentation:
# https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model

class PWidget: 
    
    def __init__(self, tag):
        self._elem = document.createElement(tag)

class PPanel(PWidget): 

    def __init__(self, rootElementId: str = None):
        super().__init__("div")
        if rootElementId != None:
            document.getElementById(rootElementId).appendChild(self._elem)
        #TODO get/insert/replace/remove individual children
        #TODO Html grid layout

    _children = []

    def getChildren(self):
        return self._children

    def removeAllChildren(self):
        self._elem.replaceChildren()
        self._children.clear()
        return self

    def addChild(self, child):
        self._elem.appendChild(child._elem)
        self._children.append(child)
        return self

class PLabel(PWidget): 
    
    def __init__(self, text):
        super().__init__("span")
        self.setText(text)

    _text = ""

    def getText(self):
        return self._text
    
    def setText(self, text):
        if text == None:
            text = ""
        if self._text != text:
            self._text = text
            self._elem.replaceChildren(document.createTextNode(self._text))
        return self

class PButton(PWidget): 

    def __init__(self, text):
        super().__init__("button")
        self.setText(text)

    _text = ""
    
    def getText(self):
        return self._text
    
    def setText(self, text):
        if text == None:
            text = ""
        if self._text != text:
            self._text = text
            self._elem.replaceChildren(document.createTextNode(self._text))
        return self

    _color = ""
    
    def getColor(self):
        return self._color

    def setColor(self, color):
        if color == None:
            color = "black"
        if self._color != color:
            self._color = color
            self._elem.setAttribute("style", f"color: {self._color}")
        return self

    _clickHandler = None
    _clickHandlerProxy = None

    def onClick(self, clickHandler):
        if self._clickHandler != clickHandler:
            if self._clickHandlerProxy != None:
                self._elem.removeEventListener("click", self._clickHandlerProxy)
            self._clickHandler = clickHandler
            self._clickHandlerProxy = create_proxy(self._clickHandler)
            self._elem.addEventListener("click", self._clickHandlerProxy)
        return self

class PEdit(PWidget): 

    def __init__(self, value):
        super().__init__("input")
        self._elem.setAttribute("type", "text")
        self.setValue(value)
    
    def getValue(self):
        return self._elem.value
    
    def setValue(self, value):
        self._elem.value = value
        return self

    _placeholder = ""
    
    def getPlaceholder(self):
        return self._placeholder

    def setPlaceholder(self, placeholder):
        if placeholder == None:
            placeholder = ""
        if self._placeholder != placeholder:
            self._placeholder = placeholder
            self._elem.setAttribute("placeholder", self._placeholder)
        return self

    _width = 100
    
    def getWidth(self):
        return self._width

    def setWidth(self, width):
        if width == None:
            width = 100
        if self._width != width:
            self._width = width
            self._elem.setAttribute("style", f"width: {self._width}px")
        #TODO All style attributes in separate dictionary, and render in a generic way
        return self
