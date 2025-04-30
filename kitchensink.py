"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

Main file
"""

from datetime import datetime
from js import fetch, JSON  # type: ignore # pylint: disable=import-error

from widgets import PGrid, PTextInput, PButton, PLabel, bind_to_dom, base_url
from todo import TodoPanel


class Main(PGrid):
    """Main class"""

    def __init__(self):
        super().__init__()
        self.set_width("100dvw")
        self.set_height("100dvh")

        self.set_rows([100, "100%", 50])
        self.set_columns([100, "60%", 100, "40%"])

        # First demo panel
        self.inp = PTextInput("").set_placeholder("press the button...")
        self.btn = PButton("Press me!").set_color("blue").on_click(self.btn_click)

        self.grd = PGrid().set_margin(6).set_row_gap(6).set_column_gap(6)
        self.grd.set_rows([36, 36, 72])
        self.grd.set_columns([100, 200, 100, 200])
        self.grd.set_areas(
            [
                [
                    PLabel("Code"),
                    PTextInput("ABC").set_pattern("[A-Z]+").set_required(True),
                    PLabel("Number"),
                    PTextInput("123").set_readonly(True),
                ],
                [PLabel("Description").set_for(self.inp), self.inp, self.inp, self.inp],
                [PLabel("Hidden").set_visible(False), None, self.btn, self.btn],
            ]
        )
        self.grd.set_border_width(2).set_border_style("dotted").set_border_color("blue")

        # Second demo panel
        self.todo = TodoPanel()

        hdr = PLabel("Header").set_color("blue")
        ftr = PLabel("Footer").set_color("green")
        self.set_areas(
            [
                [hdr, hdr, hdr, hdr],
                [
                    PLabel("Left").set_color("purple"),
                    self.grd,
                    PLabel("Middle").set_color("orange"),
                    self.todo,
                ],
                [ftr, ftr, ftr, ftr],
            ]
        )

    async def btn_click(self, event):  # pylint: disable=unused-argument
        """Button click event handler"""
        self.btn.set_color("red")
        response = await fetch(base_url() + "/assets/demo-data.json", {"method": "GET"})
        data = await response.json()
        self.inp.set_value("Now is: " + str(datetime.now()) + " " + JSON.stringify(data))

    def after_page_load(self):  # pylint: disable=useless-parent-delegation
        super().after_page_load()

        # Here, try out code after a page refresh with Live Server/Live Preview
        #self.btn.set_color("green")


if __name__ == "__main__":
    bind_to_dom(Main, "root")
