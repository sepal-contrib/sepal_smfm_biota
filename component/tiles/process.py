import biota
import numpy as np

try:
    from osgeo import gdal
except ImportError:
    import gdal

import ipyvuetify as v
from ipywidgets import Output, jslink
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
from traitlets import Bool, List, link, observe

from ..message import cm
from ..scripts.scripts import *
from ..widget.custom_widgets import *


class Process(v.Card):
    # Process widgets
    forest_p = Bool(False).tag(sync=True)
    gamma0 = Bool(False).tag(sync=True)
    biomass = Bool(False).tag(sync=True)
    forest_cov = Bool(False).tag(sync=True)
    forest_ch_p = Bool(False).tag(sync=True)
    biomass_ch = Bool(False).tag(sync=True)
    forest_ch = Bool(False).tag(sync=True)
    def_risk = Bool(False).tag(sync=True)

    # Outputs
    true_cb = List([]).tag(sync=True)

    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)

        self.param = parameters
        self.tile_1 = None
        self.tile_2 = None
        self.change_tile = None
        self.gamma0_tile = None
        self.biomass_tile = None
        self.biomass_ch_tile = None
        self.forest_ch_tile = None
        self.forest_cov_tile = None
        self.def_risk_tile = None

        self.w_alert = sw.Alert(children=[cm.alert.select_proc]).show()

        w_forest_p = v.Checkbox(
            label=cm.outputs.forest_property, class_="pl-5", v_model=self.forest_p
        )
        self.w_gamma0 = CheckboxState(label=cm.outputs.gamma, v_model=self.gamma0)
        self.w_biomass = CheckboxState(label=cm.outputs.biomass, v_model=self.biomass)
        self.w_forest_cov = CheckboxState(
            label=cm.outputs.forest_cov, v_model=self.forest_cov
        )

        w_forest_ch_p = v.Checkbox(
            label=cm.outputs.forest_ch_p, class_="pl-5", v_model=self.forest_ch_p
        )
        self.w_biomass_ch = CheckboxState(
            label=cm.outputs.biomass_ch, v_model=self.biomass_ch
        )
        self.w_forest_ch = CheckboxState(
            label=cm.outputs.ch_type, v_model=self.forest_ch
        )
        self.w_def_risk = CheckboxState(
            label=cm.outputs.def_risk, v_model=self.def_risk
        )

        w_year_1 = v.TextField(v_model=self.param.required.year_1, disabled=True)
        w_year_2 = v.TextField(v_model=self.param.required.year_2, disabled=True)

        jslink((w_year_1, "v_model"), (self.param.required, "year_1"))
        jslink((w_year_2, "v_model"), (self.param.required, "year_2"))

        # Output widgets
        self.ou_display = Output()
        self.out_dialog = v.Dialog(
            children=[v.Card(color="white", children=[self.ou_display])],
            v_model=False,
            max_width=436,
            overlay_color="black",
            overlay_opacity=0.7,
        )

        self.w_select_output = v.Select(
            class_="ps-4",
            items=self.true_cb,
            v_model=None,
            label=cm.outputs.select_label,
        )
        self.btn_process = sw.Btn(cm.buttons.get_outputs.label, class_="pl-5")

        self.btn_add_map = sw.Btn(cm.buttons.display, class_="ms-4")
        self.btn_write_raster = sw.Btn(cm.buttons.write, class_="ml-5")

        # Linked widgets

        link((w_forest_p, "v_model"), (self, "forest_p"))
        link((self.w_gamma0, "v_model"), (self, "gamma0"))
        link((self.w_biomass, "v_model"), (self, "biomass"))
        link((self.w_forest_cov, "v_model"), (self, "forest_cov"))
        link((w_forest_ch_p, "v_model"), (self, "forest_ch_p"))
        link((self.w_biomass_ch, "v_model"), (self, "biomass_ch"))
        link((self.w_forest_ch, "v_model"), (self, "forest_ch"))
        link((self.w_def_risk, "v_model"), (self, "def_risk"))

        self.year_params = v.Card(
            children=[
                sw.Tooltip(
                    v.Flex(children=[w_year_1]),
                    cm.outputs.tooltips.y1,
                    top=True,
                    bottom=False,
                ),
                w_forest_p,
                v.Divider(),
                self.w_gamma0,
                self.w_biomass,
                self.w_forest_cov,
            ]
        )

        self.change_params = v.Card(
            children=[
                sw.Tooltip(
                    v.Flex(children=[w_year_2]),
                    cm.outputs.tooltips.y2,
                    top=True,
                    bottom=False,
                ),
                w_forest_ch_p,
                v.Divider(),
                self.w_biomass_ch,
                self.w_forest_ch,
                self.w_def_risk,
            ]
        )
        self.change_params.disabled = True

        self.children = [
            v.Card(
                class_="pa-4",
                children=[
                    v.CardTitle(children=[cm.process.output_title]),
                    v.CardText(
                        class_="d-flex flex-row",
                        children=[
                            v.Col(children=[self.year_params]),
                            v.Divider(inset=True, vertical=True),
                            v.Col(children=[self.change_params]),
                        ],
                    ),
                    sw.Tooltip(
                        self.btn_process, cm.buttons.get_outputs.tooltip, bottom=True
                    ),
                ],
            ),
            self.w_alert,
            v.Card(
                class_="pb-4",
                children=[
                    self.out_dialog,
                    v.CardTitle(children=[cm.process.title_display]),
                    v.CardText(children=[cm.process.intro_display]),
                    self.w_select_output,
                    self.btn_add_map,
                    self.btn_write_raster,
                ],
            ),
        ]

        # Add all True checkBoxes to a List
        # Inspect its change

        # Decorate loading functions
        self._write_raster = su.loading_button(
            self.w_alert, self.btn_write_raster, True
        )(self._write_raster)
        self._process = su.loading_button(self.w_alert, self.btn_process, True)(
            self._process
        )
        self._display = su.loading_button(self.w_alert, self.btn_add_map, True)(
            self._display
        )

        self.btn_process.on_event("click", self._process)
        self.btn_add_map.on_event("click", self._display)
        self.btn_write_raster.on_event("click", self._write_raster)

        self.param.required.w_years.observe(self.hide_change)

    def hide_change(self, change):
        """Disable change properties if there is only one year selected."""
        if change["new"] == "Single year":
            self.change_params.disabled = True

        elif change["new"] == "Multiple year":
            self.change_params.disabled = False

    @observe("forest_ch", "gamma0", "biomass", "biomass_ch", "forest_cov", "def_risk")
    def _observe_forest_p(self, *args):
        """Get a list of current active processes (checkboxes)."""
        self._get_tiles_dictionary()
        self.true_cb = [k for k, v in self.TILES.items() if v[0] is True]

    @observe("forest_p")
    def _select_forest_property(self, change):
        """Activate/deactivate all forest property checkboxes."""
        self.gamma0 = self.biomass = self.forest_cov = change["new"]

    @observe("forest_ch_p")
    def _select_change_property(self, change):
        """Activate/deactivate all forest change checkboxes."""
        self.biomass_ch = self.forest_ch = self.def_risk = change["new"]

    def _validate_inputs(self):
        if self.param.optional.downsample_factor < 1:
            raise Exception(cm.error.assert_downsampling)

        if self.param.optional.window_size % 2 != 1:
            raise Exception(cm.error.assert_widown_size_odd)

        if self.param.required.single_year == "Multiple year":
            if self.param.required.year_1 >= self.param.required.year_2:
                raise Exception(cm.error.y1_lt_y2)

    def _load_tile(self, year):
        tile = biota.LoadTile(
            str(self.param.data_dir),
            round_(self.param.required.lat, self.param.required.grid, "lat"),
            round_(self.param.required.lon, self.param.required.grid, "lon"),
            year,
            parameter_file=self.param.PARAMETER_FILE,
            forest_threshold=self.param.optional.forest_threshold,
            area_threshold=self.param.optional.area_threshold,
            downsample_factor=self.param.optional.downsample_factor,
            lee_filter=self.param.optional.lee_filter,
            window_size=self.param.optional.window_size,
            contiguity=self.param.optional.contiguity,
            output_dir=str(self.param.output_dir),
        )
        return tile

    def _get_tiles_dictionary(self):
        # Wrap attributes, widget, and tile in a dictionary
        self.TILES = {
            # label : [attribute, widget, tile]
            cm.outputs.gamma: [self.gamma0, self.w_gamma0, self.gamma0_tile],
            cm.outputs.biomass: [self.biomass, self.w_biomass, self.biomass_tile],
            cm.outputs.forest_cov: [
                self.forest_cov,
                self.w_forest_cov,
                self.forest_cov_tile,
            ],
            cm.outputs.ch_type: [self.forest_ch, self.w_forest_ch, self.forest_ch_tile],
            cm.outputs.biomass_ch: [
                self.biomass_ch,
                self.w_biomass_ch,
                self.biomass_ch_tile,
            ],
            cm.outputs.def_risk: [self.def_risk, self.w_def_risk, self.def_risk_tile],
        }

    def _get_processed_tiles(self):
        """Get tiles that are already processed and ready for view or write."""
        self._get_tiles_dictionary()
        self.w_select_output.items = [
            name for name, v in self.TILES.items() if v[2] is not None
        ]

    def _process(self, *args):
        """Event trigger when btn_process is clicked.

        * This function is decorated by loading

        """
        # Raise error if validation doesn't pass
        self._validate_inputs()

        # Create tiles if years are selected.
        if self.param.required.year_1:
            self.tile_1 = self._load_tile(int(self.param.required.year_1))
        if self.param.required.year_2:
            self.tile_2 = self._load_tile(int(self.param.required.year_2))

        for process in self.true_cb:
            self.w_alert.reset()
            if process in ["Gamma0", "Biomass", "Forest cover"]:
                self.w_alert.type = "info"
                self.w_alert.append_msg(cm.outputs.computing.format(process))

                if process == "Gamma0":
                    self.w_gamma0.running()
                    self.gamma0_tile = self.tile_1.getGamma0(
                        polarisation=self.param.optional.polarisation, units="decibels"
                    )
                    self.w_gamma0.done()
                elif process == "Biomass":
                    self.w_biomass.running()
                    self.biomass_tile = self.tile_1.getAGB()
                    self.w_biomass.done()

                elif process == "Forest cover":
                    self.w_forest_cov.running()
                    self.forest_cov_tile = self.tile_1.getWoodyCover()
                    self.w_forest_cov.done()

                self.w_alert.append_msg(cm.outputs.ready.format(process))
                self.w_alert.type = "success"

            elif process in ["Biomass change", "Change type", "Deforestation risk"]:
                self.w_alert.add_msg(cm.outputs.retrieving_ch)
                assert all(
                    (self.param.required.year_1, self.param.required.year_2)
                ), assert_errors(self, cm.error.both_years)
                # Compute change tile
                self.change_tile = biota.LoadChange(
                    self.tile_1,
                    self.tile_2,
                    change_area_threshold=self.param.optional.change_area_threshold,
                    change_magnitude_threshold=self.param.optional.change_magnitude_threshold,
                    contiguity=self.param.optional.contiguity,
                )

                self.w_alert.add_msg(cm.outputs.computing.format(process))
                self.w_alert.type_ = "info"

                if process == "Biomass change":
                    self.w_biomass_ch.running()
                    self.biomass_ch_tile = self.change_tile.getAGBChange()
                    self.w_biomass_ch.done()

                elif process == "Change type":
                    self.w_forest_ch.running()
                    self.change_tile.getChangeType()
                    self.forest_ch_tile = self.change_tile.ChangeCode
                    self.w_forest_ch.done()

                elif process == "Deforestation risk":
                    self.w_def_risk.running()
                    self.def_risk_tile = self.change_tile.getRiskMap()
                    self.w_def_risk.done()

                self.w_alert.append_msg(cm.outputs.ready.format(process))
                self.w_alert.type = "success"
            else:
                self.w_alert.append_msg(cm.error.at_least_process)

        # Update state of display/write select widget
        self._get_processed_tiles()

    def _write_raster(self, *args):
        """Write processed raster.

        * This function is decorated by loading

        Args:
            widget (ipywidgets): w_select_output with list of possible processed rasters (self.TILES)

        """
        # Get current raster tile name
        tile_name = self.w_select_output.v_model

        # Get tile from selected dropdown
        self._get_tiles_dictionary()
        tile = self.TILES[tile_name][2]
        assert tile is not None, assert_errors(
            self, cm.error.before_write.format(tile_name)
        )

        if tile_name in ["Biomass", "Gamma0", "Biomass change", "Deforestation risk"]:
            self.tile_1._LoadTile__outputGeoTiff(tile, tile_name)

        elif tile_name in ["Change type", "Forest cover"]:
            self.tile_1._LoadTile__outputGeoTiff(tile, tile_name, dtype=gdal.GDT_Byte)

        self.w_alert.add_msg(
            cm.alert.success_export.format(tile_name, self.param.output_dir),
            type_="success",
        )

    def _display(self, *args):
        """Display processed raster.

        * This function is decorated by loading

        Args:
            widget (ipywidgets): w_select_output with list of possible processed rasters (self.TILES)

        """
        # Get current raster tile name
        tile_name = self.w_select_output.v_model

        # Get tile from selected dropdown
        self._get_tiles_dictionary()
        tile = self.TILES[tile_name][2]
        assert tile is not None, assert_errors(
            self, cm.error.before_display.format(tile_name)
        )

        with self.ou_display:
            self.ou_display.clear_output()
            if tile_name == "Biomass":
                title, cbartitle, vmin, vmax, cmap = "AGB", "tC/ha", 0, 40, "YlGn"
            elif tile_name == "Gamma0":
                title, cbartitle, vmin, vmax, cmap = (
                    f"Gamma0 {self.param.optional.polarisation}",
                    "decibels",
                    -20,
                    -10,
                    "Greys_r",
                )
            elif tile_name == "Forest cover":
                title, cbartitle, vmin, vmax, cmap = (
                    "Woody Cover",
                    "decibels",
                    0,
                    1,
                    "summer_r",
                )

            elif tile_name == "Biomass change":
                title, cbartitle, vmin, vmax, cmap = (
                    "AGB Change",
                    "tC/ha",
                    -10,
                    10,
                    "YlGn",
                )

            elif tile_name == "Change type":
                # Hide minor gain, minor loss and nonforest in display output
                change_code_display = np.ma.array(
                    tile, mask=np.zeros_like(tile, dtype=bool)
                )
                change_code_display.mask[
                    np.isin(change_code_display, [0, 3, 4, 255])
                ] = True

                # Overwrite current tile with new change_code_display
                tile, title, cbartitle, vmin, vmax, cmap = (
                    change_code_display,
                    "Change type",
                    "Type",
                    1,
                    6,
                    "Spectral",
                )

            elif tile_name == "Deforestation risk":
                title, cbartitle, vmin, vmax, cmap = (
                    "Deforestation risk map",
                    "Low - High risk",
                    0,
                    3,
                    "autumn",
                )

            # Show arrays with showArray method from LoadTile object
            # We are just using this method to display any tile with the given UI.lat and UI.lon
            self.tile_1._LoadTile__showArray(tile, title, cbartitle, vmin, vmax, cmap)
            self.out_dialog.v_model = True
