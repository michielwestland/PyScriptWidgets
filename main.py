"""Main file"""

from datetime import datetime
from js import fetch, JSON  # type: ignore # pylint: disable=import-error
from widgets import PPanel, PGrid, PTextInput, PButton, PLabel, bind_to_dom
from todo import TodoPanel

# Set the base url when deploying to: https://michielwestland.github.io/PyScriptWidgets
BASE_URL = "."


class Main(PPanel):
    """Main class"""

    def __init__(self):
        super().__init__(True)
        self.inp = PTextInput("").set_placeholder("press the button...")
        self.btn = PButton("Press me!").set_color("blue").on_click(self.btn_click)

        self.grd = PGrid().set_margin(6).set_gap(6)
        self.grd.set_rows([36, 36, 72])
        self.grd.set_columns([100, 200, 100, 200])
        self.grd.set_areas(
            [
                [
                    PLabel("Code"),
                    PTextInput("ABC").set_required(True),
                    PLabel("Number"),
                    PTextInput("123").set_readonly(True),
                ],
                [PLabel("Description").set_for(self.inp), self.inp, self.inp, self.inp],
                [PLabel("Hidden").set_visible(False), None, self.btn, self.btn],
            ]
        )
        self.add_child(self.grd)

        self.todo_pnl = TodoPanel()
        self.add_child(self.todo_pnl)

        span_btn1 = PButton("Span1")
        span_btn2 = PButton("Span2")
        self.wide_grd = PGrid()
        self.wide_grd.set_min_width(1000)
        self.wide_grd.set_rows([36, 36, 36])
        self.wide_grd.set_columns(
            [
                90,
                "calc(25 * (100% - 180px) / 100)",
                "calc(75 * (100% - 180px) / 100)",
                90,
            ]
        )
        self.wide_grd.set_areas(
            [
                [span_btn1, span_btn1, span_btn1, span_btn1],
                [
                    PLabel("Left side"),
                    PButton("Small 25% button"),
                    PButton("Wide 75% button"),
                    PLabel("Right side"),
                ],
                [span_btn2, span_btn2, span_btn2, span_btn2],
            ]
        )
        self.add_child(self.wide_grd)

    async def btn_click(self, event):  # pylint: disable=unused-argument
        """Button click event handler"""
        self.btn.set_color("red")
        response = await fetch("./data.json", {"method": "GET"})
        data = await response.json()
        self.inp.set_value("Now is: " + str(datetime.now()) + " " + JSON.stringify(data))

    def after_page_load(self):
        super().after_page_load()
        # Here, try out code after a page refresh with Live Server/Live Preview
        self.btn.set_color("green")


if __name__ == "__main__":
    bind_to_dom(Main, "root")
