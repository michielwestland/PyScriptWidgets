"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

Main file
"""

import js  # pylint: disable=import-error

# from pyscript.js_modules.JQuery import default as jq  # type: ignore # pylint: disable=import-error

from widgets import PGrid, PLabel, PTab, PPanel, bind_to_dom


# TODO Also set dark mode off: globals.py; _main_widget.set_dark_mode(False)


class Test(PGrid):
    """Main class"""

    def __init__(self):
        super().__init__()
        self.set_width("100dvw")
        self.set_height("100dvh")

        self.set_rows(["50%", 500, "50%"])
        self.set_columns(["50%", 250, "100%"])

        self.tab = PTab()

        self.set_areas(
            [
                [PLabel(""), PLabel(""), PLabel("")],
                [
                    PLabel(""),
                    self.tab,
                    PLabel(""),
                ],
                [PLabel(""), PLabel(""), PLabel("")],
            ]
        )

        self.tab.add_tab("First")
        tab_first = PPanel(False)
        tab_first.add_child(PLabel("Contents 1"))
        tab_first._elem.classList.add("ui")
        tab_first._elem.classList.add("bottom")
        tab_first._elem.classList.add("attached")
        tab_first._elem.classList.add("tab")
        tab_first._elem.classList.add("segment")
        tab_first._elem.dataset.tab = 0
        self.tab.add_child(tab_first)

        self.tab.add_tab("Second")
        tab_second = PPanel(False)
        tab_second.add_child(PLabel("Contents 2"))
        tab_second._elem.classList.add("ui")
        tab_second._elem.classList.add("bottom")
        tab_second._elem.classList.add("attached")
        tab_second._elem.classList.add("tab")
        tab_second._elem.classList.add("segment")
        tab_second._elem.dataset.tab = 1
        self.tab.add_child(tab_second)

        self.tab.set_active(0)

    def after_page_load(self):  # pylint: disable=useless-parent-delegation
        super().after_page_load()

        # jq(".menu .item").tab()
        js.ptab_init()


if __name__ == "__main__":
    bind_to_dom(Test, "root")
