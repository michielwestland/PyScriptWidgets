"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


from widgets.base import *
from widgets.button import *
from widgets.compound import *
from widgets.focussable import *
from widgets.globals import *
from widgets.grid import *
from widgets.input import *
from widgets.label import *
from widgets.panel import *
from widgets.text import *


# TODO Add a resize listener to the browser window object. Onresize eventhandler on main widget.
# See: https://developer.mozilla.org/en-US/docs/Web/API/Window/resize_event

# TODO Add a form widget that wraps labels/inputs with divs for error state and that shows error messages.
# See: https://semantic-ui.com/collections/form.html

# TODO Make a progressive web application (PWA).
# See: https://github.com/jhanley-com/pyscript_pwa_demo_1
# See: https://github.com/Oussama1403/Pyscript-Offline
# See: https://pyscript.com/docs/pwa

# TODO Add a SVG widget and widgets for basic shapes using the DOM tree.

# TODO Add widget border property or border component.

# TODO Add widget background image/linear gradient property: linear-gradient(to bottom right, #F0F8FF, white);

# TODO Add image widget.

# TODO Add hyperlink widget.

# TODO Implement number input, format value, properties: min, max, step and decimals
#class PNumberInput(PInputWidget):    """Number input widget class"""

# TODO Implement date input, format value, input types: date, time, datetime-local
#class PDateInput(PInputWidget):    """Date input widget class"""

# TODO Implement checkbox, see: https://semantic-ui.com/modules/checkbox.html
#class PCheckBox(PInputWidget):    """Checkbox widget class"""

# TODO Implement radio group, see: https://semantic-ui.com/modules/checkbox.html#radio
#class PRadioGroup(PCompoundWidget):    """Radio group widget class"""

# TODO Implement combo box, see: https://semantic-ui.com/modules/dropdown.html
#class PComboBox(PCompoundWidget):    """Combobox widget class"""

# TODO Implement menu item, see: https://semantic-ui.com/collections/menu.html
#class PMenuItem(PWidget):    """Menu item widget class"""

# TODO Implement menu, see: https://semantic-ui.com/collections/menu.html#menu
#class PMenu(PCompoundWidget):    """Menu widget class"""

# TODO Implement menu bar, see: https://semantic-ui.com/collections/menu.html#sub-menu
#class PMenuBar(PCompoundWidget):    """Menu bar widget class"""

# TODO Implement table, see: https://semantic-ui.com/collections/table.html
#class PTable(PCompoundWidget):    """Table widget class"""

# TODO Implement tab pane, see: https://semantic-ui.com/modules/tab.html
#class PTabPane(PCompoundWidget):    """Tab pane widget class"""

# TODO Implement text area.
#class PTextArea(PFocussableWidget):    """Text area widget class"""

# TODO Implement modal widget, see: https://semantic-ui.com/modules/modal.html
#class PModal(PCompoundWidget):    """Modal dialog widget class"""
