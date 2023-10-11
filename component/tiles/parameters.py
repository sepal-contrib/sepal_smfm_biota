import os
from datetime import datetime

import ipyvuetify as v
from biota import download as dw
from ipywidgets import Output
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
from traitlets import Bool, CFloat, CInt, Float, Int, Unicode, link

from component.message import cm
from component.parameter import *
from component.scripts.scripts import *
from component.widget import *


class Parameters(v.Layout):
    def __init__(self, **kwargs):

        # Widget classes
        self.class_ = "flex-column pa-2"
        self.row = True
        self.xs12 = True

        super().__init__(**kwargs)

        # Parameters
        self.root_dir = root_dir
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.PARAMETER_FILE = parameter_file

        self.map_tile = MapTile(parameters=self)

        # Set up process parameters
        self.required = Required(class_="pa-4")
        self.optional = Optional(class_="pa-4")

        # Alerts
        self.w_alert = sw.Alert(children=[cm.param.sel_param]).show()
        self.ou_progress = Output()

        self.progress_alert = sw.Alert(children=[self.ou_progress]).hide()

        self.children = [
            v.Card(
                children=[
                    v.CardTitle(children=[cm.process.header_title]),
                    v.CardText(children=[cm.process.header_text]),
                ]
            ),
            v.Row(
                class_="d-flex flex-row ",
                xs12=True,
                md6=True,
                children=[
                    v.Col(
                        children=[
                            Tabs(
                                ["Required inputs", "Optional inputs"],
                                [self.required, self.optional],
                            )
                        ]
                    ),
                    v.Col(children=[self.map_tile]),
                ],
            ),
            v.Card(
                class_="flex-row pa-2 mb-3",
                children=[self.w_alert, self.progress_alert],
            ),
        ]

        # Decorate self._download() method
        self._download = su.loading_button(
            self.w_alert, self.required.w_download, debug=True
        )(self._download)

        # Events
        self.required.w_download.on_event("click", self._download_event)

    def _download_event(self, *args):

        years = [
            int(year) for year in [self.required.year_1, self.required.year_2] if year
        ]
        lat = round_(self.required.lat, self.required.grid, "lat")
        lon = round_(self.required.lon, self.required.grid, "lon")
        assert years != [], assert_errors(self, cm.error.at_least_year)

        with self.ou_progress:

            self.ou_progress.clear_output()
            self.progress_alert.show()

            for y in years:
                try:
                    self.progress_alert.type = "info"
                    self._download(lat, lon, y)
                    self.progress_alert.type = "success"
                except:
                    pass

    def _download(self, *args):

        lat, lon, y = args
        self.w_alert.add_msg(cm.alert.downloading.format(y, lat, lon), type_="info")

        large_tile = True
        if self.required.grid == 1:
            large_tile = False

        try:
            dw.download(
                lat,
                lon,
                y,
                large_tile=large_tile,
                output_dir=self.data_dir,
                verbose=True,
            )
        except ValueError as e:
            if "already exists" in next(iter(e.args)):
                # To those files that were downloaded but un-decompressed
                pass

        self.w_alert.add_msg(cm.alert.decompressing.format(y), type_="info")
        self._decompress()

        self.w_alert.add_msg(cm.alert.done_down.format(y, lat, lon), type_="success")

    def _decompress(self):

        tar_files = list(self.data_dir.glob("*.tar.gz")) + list(
            self.data_dir.glob("*.zip")
        )

        for tar in tar_files:
            if not os.path.exists(os.path.join(self.data_dir, tar.name[:-7])):
                self.w_alert.add_msg(
                    cm.alert.decompressingtar.format(tar.name), type_="info"
                )
                try:
                    # If there's not file, it will raise an exception and will stop the execution
                    dw.decompress(str(tar))
                    self.w_alert.add_msg(cm.alert.done_unzip, type_="success")
                except:
                    continue


class Select(v.Select, sw.SepalWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Required(v.Card):

    # Initial widgets
    lat = Float(0).tag(sync=True)
    lon = Float(-75).tag(sync=True)
    year_1 = Unicode("2016").tag(sync=True)
    year_2 = Unicode("").tag(sync=True)
    grid = Int(1).tag(sync=True)
    single_year = Unicode("Single year").tag(sync=True)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # 1. .Input widgets (Parameters)
        w_lat = v.TextField(
            disabled=True,
            label=cm.param.req.latitude,
            v_model=self.lat,
        )
        w_lon = v.TextField(
            disabled=True,
            label=cm.param.req.longitude,
            v_model=self.lon,
        )

        w_lat_tooltip = sw.Tooltip(w_lat, cm.tooltip.coordinates)
        w_lon_tooltip = sw.Tooltip(w_lon, cm.tooltip.coordinates)

        # Ask if user wants to compute only one year
        self.w_years = v.RadioGroup(
            label="Type of analysis",
            row=True,
            v_model=self.single_year,
            children=[
                v.Radio(key=1, label="Single year", value="Single year"),
                v.Radio(key=2, label="Multiple year", value="Multiple year"),
            ],
        )

        # Valid years for selection
        self.valid_years = [
            str(y)
            for y in list(range(2007, 2010 + 1))
            + list(range(2015, datetime.now().year + 1))
        ]

        self.w_year_1 = v.Select(
            label=cm.param.req.year1,
            items=self.valid_years,
            type="number",
            v_model=self.year_1,
        )
        self.w_year_2 = Select(
            label=cm.param.req.year2,
            items=self.valid_years,
            type="number",
            v_model=self.year_2,
        ).hide()

        w_grid = v.RadioGroup(
            v_model=self.grid,
            children=[
                v.Radio(label=cm.param.req._1grid, value=1),
                #             v.Radio(label=cm.param.req._5grid, value=5)
            ],
        )

        self.w_download = sw.Btn(cm.param.req.download, class_="pl-5")

        link((w_lon, "v_model"), (self, "lon"))
        link((w_lat, "v_model"), (self, "lat"))
        link((self.w_year_1, "v_model"), (self, "year_1"))
        link((self.w_year_2, "v_model"), (self, "year_2"))
        link((w_grid, "v_model"), (self, "grid"))

        self.children = [
            v.CardText(children=[cm.param.req.description]),
            w_lon_tooltip,
            w_lat_tooltip,
            self.w_years,
            self.w_year_1,
            self.w_year_2,
            w_grid,
            self.w_download,
        ]

        self.w_years.observe(self.on_single_change, "v_model")

    def on_single_change(self, change):

        if change["new"] == "Single year":
            su.hide_component(self.w_year_2)
            self.year_2 = ""

        elif change["new"] == "Multiple year":

            su.show_component(self.w_year_2)
            current_year = datetime.now().year

            if int(self.year_1) < current_year:
                self.year_2 = self.valid_years[self.valid_years.index(self.year_1) + 1]
            else:
                self.year_2 = self.year_1


class Optional(v.Card):

    lee_filter = Bool(True).tag(sync=True)

    downsample_factor = CInt(1).tag(sync=True)
    window_size = CInt(5).tag(sync=True)
    forest_threshold = CFloat(10.0).tag(sync=True)
    area_threshold = CFloat(0.0).tag(sync=True)
    change_area_threshold = CInt(2).tag(sync=True)
    change_magnitude_threshold = CInt(15).tag(sync=True)

    contiguity = Unicode("queen").tag(sync=True)
    #     sm_interpolation = Unicode('average').tag(sync=True)
    polarisation = Unicode("HV").tag(sync=True)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        w_lee_filter = v.Checkbox(
            label=cm.param.opt.lee_filter.name, v_model=self.lee_filter
        )
        w_downsample_factor = v.TextField(
            label=cm.param.opt.downsample_factor.name,
            type="number",
            v_model=self.downsample_factor,
        )
        w_window_size = v.TextField(
            label=cm.param.opt.window_size.name, type="number", v_model=self.window_size
        )
        w_forest_threshold = v.TextField(
            label=cm.param.opt.forest_threshold.name,
            type="number",
            v_model=self.forest_threshold,
        )
        w_area_threshold = v.TextField(
            label=cm.param.opt.area_threshold.name,
            type="number",
            v_model=self.area_threshold,
        )
        w_change_area_threshold = v.TextField(
            label=cm.param.opt.change_area_threshold.name,
            type="number",
            v_model=self.change_area_threshold,
        )
        w_change_magnitude_threshold = v.TextField(
            label=cm.param.opt.change_magnitude_threshold.name,
            type="number",
            v_model=self.change_magnitude_threshold,
        )
        w_contiguity = v.Select(
            label=cm.param.opt.contiguity.name,
            items=["rook", "queen"],
            v_model=self.contiguity,
        )
        #         w_sm_interpolation = v.Select(
        #             label=cm.param.opt.sm_interpolation, items=['nearest', 'average', 'cubic'], v_model=self.sm_interpolation)
        w_polarisation = v.Select(
            label=cm.param.opt.polarisation.name,
            items=["HV", "HH", "VV", "VH"],
            v_model=self.polarisation,
        )

        link((w_lee_filter, "v_model"), (self, "lee_filter"))

        link((w_downsample_factor, "v_model"), (self, "downsample_factor"))
        link((w_window_size, "v_model"), (self, "window_size"))
        link((w_forest_threshold, "v_model"), (self, "forest_threshold"))
        link((w_area_threshold, "v_model"), (self, "area_threshold"))

        link((w_change_area_threshold, "v_model"), (self, "change_area_threshold"))
        link(
            (w_change_magnitude_threshold, "v_model"),
            (self, "change_magnitude_threshold"),
        )

        link((w_contiguity, "v_model"), (self, "contiguity"))
        #         link((w_sm_interpolation, 'v_model'),(self, 'sm_interpolation'))
        link((w_polarisation, "v_model"), (self, "polarisation"))

        self.children = [
            sw.Tooltip(
                w_lee_filter,
                cm.param.opt.lee_filter.tooltip,
                bottom=True,
                max_width=300,
            ),
            sw.Tooltip(
                w_window_size,
                cm.param.opt.window_size.tooltip,
                bottom=True,
                max_width=300,
            ),
            sw.Tooltip(
                w_downsample_factor,
                cm.param.opt.downsample_factor.tooltip,
                bottom=True,
                max_width=300,
            ),
            sw.Tooltip(
                w_forest_threshold,
                cm.param.opt.forest_threshold.tooltip,
                bottom=True,
                max_width=300,
            ),
            sw.Tooltip(
                w_area_threshold,
                cm.param.opt.area_threshold.tooltip,
                bottom=True,
                max_width=300,
            ),
            sw.Tooltip(
                w_change_area_threshold,
                cm.param.opt.change_area_threshold.tooltip,
                bottom=True,
                max_width=300,
            ),
            sw.Tooltip(
                w_change_magnitude_threshold,
                cm.param.opt.change_magnitude_threshold.tooltip,
                bottom=True,
                max_width=300,
            ),
            sw.Tooltip(
                w_contiguity,
                cm.param.opt.contiguity.tooltip,
                bottom=True,
                max_width=300,
            ),
            sw.Tooltip(
                w_polarisation,
                cm.param.opt.polarisation.tooltip,
                bottom=True,
                max_width=300,
            ),
            #             w_sm_interpolation,
        ]
