"""
Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

PyScriptWidgets - A client side GUI class (widget) library for building web applications with PyScript.
"""


from widgets.compound import PCompoundWidget
from widgets.panel import PPanel


class PGrid(PCompoundWidget):
    """Grid widget class with grid layout obviously"""

    def __init__(self):
        """Constructor, define tag and class attributes"""
        super().__init__("div")
        self._insert_display()
        # Properties
        self._columns = []
        self._render_columns()
        self._rows = []
        self._render_rows()
        self._areas = ""
        self._render_areas()

    def _insert_state(self):
        """Override this method to insert state, for keys that could not be pickled"""
        super()._insert_state()
        self._insert_display()

    def restore_state(self):
        """Override this method to restore runtime DOM state from widget instance fields after unpickling from session storage"""
        super().restore_state()
        # Properties
        self._render_columns()
        self._render_rows()
        self._render_areas()

    def _insert_display(self):
        # See: https://grid.malven.co
        self._elem.style.display = "grid"
        self._elem.style.alignItems = "baseline"

    # Property: columns
    def _render_columns(self):
        """Renderer"""
        all_perc_px = len(self._columns) > 0
        total_px = 0
        for c in self._columns:
            all_perc_px = all_perc_px and (c.endswith("%") or c.endswith("px"))
            if c.endswith("px"):
                total_px += int(c[:-2])
        if all_perc_px:
            # When there are only 'px' and '%' values, convert percentages to a calculation of the percentage of *remaining* space
            arr = []
            for c in self._columns:
                if c.endswith("%"):
                    perc = int(c[:-1])
                    arr.append("calc(" + c + " - " + str(perc * total_px / 100) + "px)")
                else:
                    arr.append(c)
            self._elem.style.gridTemplateColumns = " ".join(arr)
        else:
            self._elem.style.gridTemplateColumns = " ".join(self._columns)

    def get_columns(self):
        """Accessor"""
        return self._columns

    def set_columns(self, columns):
        """Mutator"""
        for index, value in enumerate(columns):
            try:
                pixels = int(value)  # Integer values as a convenience
                columns[index] = str(pixels) + "px"
            except ValueError:
                pass  # It was not an integer value

        if self._columns != columns:
            self._columns = columns
            self._render_columns()
        return self

    # Property: rows
    def _render_rows(self):
        """Renderer"""
        all_perc_px = len(self._rows) > 0
        total_px = 0
        for r in self._rows:
            all_perc_px = all_perc_px and (r.endswith("%") or r.endswith("px"))
            if r.endswith("px"):
                total_px += int(r[:-2])
        if all_perc_px:
            # When there are only 'px' and '%' values, convert percentages to a calculation of the percentage of *remaining* space
            arr = []
            for r in self._rows:
                if r.endswith("%"):
                    perc = int(r[:-1])
                    arr.append("calc(" + r + " - " + str(perc * total_px / 100) + "px)")
                else:
                    arr.append(r)
            self._elem.style.gridTemplateRows = " ".join(arr)
        else:
            self._elem.style.gridTemplateRows = " ".join(self._rows)

    def get_rows(self):
        """Accessor"""
        return self._rows

    def set_rows(self, rows):
        """Mutator"""
        for index, value in enumerate(rows):
            try:
                pixels = int(value)  # Integer values as a convenience
                rows[index] = str(pixels) + "px"
            except ValueError:
                pass  # It was not an integer value

        if self._rows != rows:
            self._rows = rows
            self._render_rows()
        return self

    # Property: areas (readonly)
    def _render_areas(self):
        """Renderer"""
        self._elem.style.gridTemplateAreas = self._areas

    def set_areas(self, areas):
        """Mutator"""
        # See: https://www.w3schools.com/css/css_grid.asp
        # See: https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas
        self.remove_all_children()

        self._areas = ""
        for line in areas:

            area_row = ""
            for c in line:
                if c is None:
                    area_row += " ."
                else:
                    if not c in self.get_children():
                        self.add_child(c)
                    area_row += " " + c._widget_id  # pylint: disable=protected-access

            if len(area_row) > 0:
                area_row = area_row[1:]
            self._areas += " " + '"' + area_row + '"'

        if len(self._areas) > 0:
            self._areas = self._areas[1:]
        self._render_areas()

    def add_child(self, child):
        """Add a single child"""
        if isinstance(child, (PPanel, PGrid)):
            child._elem.style.overflow = "auto"  # pylint: disable=protected-access
            child.set_max_width("100%")
            child.set_max_height("100%")
        return super().add_child(child)
