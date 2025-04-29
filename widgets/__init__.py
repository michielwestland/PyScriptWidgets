"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


from widgets.base import *  # pylint: disable=unused-import
from widgets.button import *  # pylint: disable=unused-import
from widgets.compound import *  # pylint: disable=unused-import
from widgets.focussable import *  # pylint: disable=unused-import
from widgets.globals import *  # pylint: disable=unused-import
from widgets.grid import *  # pylint: disable=unused-import
from widgets.input import *  # pylint: disable=unused-import
from widgets.label import *  # pylint: disable=unused-import
from widgets.panel import *  # pylint: disable=unused-import
from widgets.text import *  # pylint: disable=unused-import


# TODO Add a resize listener to the browser window object. Onresize eventhandler on main widget.
# See: https://developer.mozilla.org/en-US/docs/Web/API/Window/resize_event

# TODO Add a form widget that wraps labels/inputs with divs for error state and that shows error messages.
# See: https://fomantic-ui.com/collections/form.html

# TODO Make a progressive web application (PWA).
# See: https://github.com/jhanley-com/pyscript_pwa_demo_1
# See: https://github.com/Oussama1403/Pyscript-Offline
# See: https://pyscript.com/docs/pwa

# TODO Add a SVG widget and widgets for basic shapes using the DOM tree.

# TODO Implement canvas widget.

# TODO Implement image widget.
#class PImage(PBaseWidget): """Image widget class"""

# TODO Implement hyperlink widget. Always target a new browser tab/window
#class PHyperlink(PBaseWidget): """Hyperlink widget class"""

# TODO Implement text area.
#class PTextArea(PFocussableWidget): """Text area widget class"""

# TODO Implement number input, format value, properties: min, max, step and decimals
#class PNumberInput(PInputWidget): """Number input widget class"""

# TODO Implement date input, format value, input types: date, time, datetime-local
#class PDateInput(PInputWidget): """Date input widget class"""

# TODO Implement checkbox, see: https://fomantic-ui.com/modules/checkbox.html
#class PCheckBox(PInputWidget): """Checkbox widget class"""

# TODO Implement radio group, see: https://fomantic-ui.com/modules/checkbox.html#radio
#class PRadioGroup(PCompoundWidget): """Radio group widget class"""

# TODO Implement combo box, see: https://fomantic-ui.com/modules/dropdown.html
#class PComboBox(PCompoundWidget): """Combobox widget class"""

# TODO Implement menu item, see: https://fomantic-ui.com/collections/menu.html
#class PMenuItem(PBaseWidget): """Menu item widget class"""

# TODO Implement menu, see: https://fomantic-ui.com/collections/menu.html#menu
#class PMenu(PCompoundWidget): """Menu widget class"""

# TODO Implement menu bar, see: https://fomantic-ui.com/collections/menu.html#sub-menu
#class PMenuBar(PCompoundWidget): """Menu bar widget class"""

# TODO Implement table, see: https://fomantic-ui.com/collections/table.html
#class PTable(PCompoundWidget): """Table widget class"""

# TODO Implement tab pane, see: https://fomantic-ui.com/modules/tab.html
#class PTabPane(PCompoundWidget): """Tab pane widget class"""

# TODO Implement modal widget, see: https://fomantic-ui.com/modules/modal.html
#class PModal(PCompoundWidget): """Modal dialog widget class"""
