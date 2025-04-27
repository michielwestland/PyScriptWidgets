"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


import base64
import pickle
import zlib

from js import console, sessionStorage  # type: ignore # pylint: disable=import-error
# Prefer pyscript import over more basic js import for the document and window objects
from pyscript import document, window  # type: ignore # pylint: disable=import-error
from pyodide.ffi.wrappers import add_event_listener  # type: ignore # pylint: disable=import-error


# Constants
_STATE_KEY = "widget_state"
_ID_PREFIX = "e"
_ID_SUPPLEMENT = "_"
_UTF_8 = "utf-8"


# Private global reference to the root widget
_main_widget = None  # pylint: disable=invalid-name


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
