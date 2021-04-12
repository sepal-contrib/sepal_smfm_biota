from functools import partial
import numpy as np
import gdal

import biota

from ipywidgets import Output
import ipyvuetify as v
from traitlets import (
    Bool, List, link
)
from sepal_ui import sepalwidgets as sw


from ..message import cm
from ..scripts.scripts import *
from ..widget.custom_widgets import *

class Process(v.Card):

    # Process widgets
    forest_p = Bool(False).tag(sync=True)
    forest_ch = Bool(False).tag(sync=True)
    gamma0 = Bool(False).tag(sync=True)
    biomass = Bool(False).tag(sync=True)
    biomass_ch = Bool(False).tag(sync=True)
    forest_cv = Bool(False).tag(sync=True)
    
    # Outputs
    true_cb = List([]).tag(sync=True)
    
    def __init__(self, parameters, **kwargs):
        
        self.param = parameters
        self.tile_1 = None
        self.tile_2 = None
        self.change_tile = None
        
        self.gamma0_tile = None
        self.agb_tile = None
        self.biomass_change_tile = None
        self.forest_change_code = None
        
        self._observe_forest_p()
        
        super().__init__(**kwargs)
        
        
        self.w_alert = Alert(children=[cm.alert.select_proc]).show()
        
        w_forest_p = v.Checkbox(label=cm.outputs.forest_property, class_='pl-5', v_model=self.forest_p, disabled=True)
        w_forest_ch = v.Checkbox(label=cm.outputs.ch_type, class_='pl-5', v_model=self.forest_ch)
        w_gamma0 = v.Checkbox(label=cm.outputs.gamma, class_='pl-5', v_model=self.gamma0)
        w_biomass = v.Checkbox(label=cm.outputs.biomass, class_='pl-5', v_model=self.biomass)
        w_biomass_ch = v.Checkbox(label=cm.outputs.biomass_ch, class_='pl-5', v_model=self.biomass_ch)
        w_forest_cv = v.Checkbox(label=cm.outputs.forest_cov, class_='pl-5', v_model=self.forest_cv, disabled=True)
        
        # Output widgets
        self.ou_display = Output()
        self.out_dialog = v.Dialog(
            children=[v.Card(color='white', children=[self.ou_display])], 
            v_model=False, 
            max_width=436,
            overlay_color='black', 
            overlay_opacity=0.7
        )
        
        self.w_select_output = v.Select(
            class_='ps-4',
            items=self.true_cb, 
            v_model=None, 
            label=cm.outputs.select_label)
        self.btn_process = sw.Btn(cm.buttons.get_outputs, class_='pl-5')
        
        self.btn_add_map = sw.Btn(cm.buttons.display, class_='ms-4')
        self.btn_write_raster = sw.Btn(cm.buttons.write, class_='ml-5')
        
        # Linked widgets

        link((w_forest_p, 'v_model'), (self, 'forest_p'))
        link((w_forest_ch, 'v_model'), (self, 'forest_ch'))
        link((w_gamma0, 'v_model'), (self, 'gamma0'))
        link((w_biomass, 'v_model'), (self, 'biomass'))
        link((w_biomass_ch, 'v_model'), (self, 'biomass_ch'))
        link((w_forest_cv, 'v_model'), (self, 'forest_cv'))
        link((self.w_select_output, 'items'), (self, 'true_cb'))
        
        self.btn_process.on_event('click', partial(self._event, func=self._process))
        self.btn_add_map.on_event('click', partial(self._event, func=self._display))
        self.btn_write_raster.on_event('click', partial(self._event, func=self._write_raster))
        
        self.children=[v.Card(children=[
                v.CardTitle(children=[cm.process.output_title]),
                v.CardText(class_="d-flex flex-row", children=[
                    v.Col(children=[w_forest_p,w_forest_ch,]),
                    v.Col(children=[w_gamma0,w_biomass,]),
                    v.Col(children=[w_forest_cv, w_biomass_ch,]),
                    self.btn_process
                ])
            ]),
            self.w_alert,
            v.Card(
                class_='pb-4',
                children=[
                    self.out_dialog,
                    v.CardTitle(children=[cm.process.title_display]), 
                    v.CardText(children=[cm.process.intro_display]),
                    self.w_select_output, 
                    self.btn_add_map,
                    self.btn_write_raster])
        ]

        # Add all True checkBoxes to a List
        # Inspect its change
    
        # Decorate loading functions
        self._write_raster = loading(self.btn_write_raster, self.w_alert)(self._write_raster)
        self._process = loading(self.btn_process, self.w_alert)(self._process)
        self._display = loading(self.btn_add_map, self.w_alert)(self._display)
    
    
    def _event(self, widget, event, data, func):
        """ This function is used to execute decorated 
        functions with an event
        
        example:
            
            btn.on_event('click', partial(self._event, func=self._process))
            where self._process is the decorated function to be executed.
        
        """
        func()
    
    @observe('forest_p', 'forest_ch', 'gamma0', 
             'biomass', 'biomass_ch', 'forest_cv')
    def _observe_forest_p(self, change=None):
        labels = {
            cm.outputs.forest_property : self.forest_p,
            cm.outputs.ch_type : self.forest_ch,
            cm.outputs.gamma : self.gamma0,
            cm.outputs.biomass : self.biomass,
            cm.outputs.biomass_ch : self.biomass_ch,
            cm.outputs.forest_cov : self.forest_cv
        }

        self.true_cb = [k for k, v in labels.items() if v is True]
        
    
    def _validate_inputs(self):
        
        assert (self.param.required.year_1 != '') or (self.param.required.year_2 != ''), assert_errors(self, cm.error.at_least_year)
        assert self.param.required.lat < 90. or self.param.required.lat > -90., assert_errors(self, cm.error.assert_latitude)
        assert self.param.required.lon < 180. or self.param.required.lon > -180., assert_errors(self, cm.error.assert_longitude)
        assert self.param.optional.downsample_factor >= 1 and type(self.param.optional.downsample_factor) == int, assert_errors(self, cm.error.assert_downsampling)
        assert type(self.param.optional.lee_filter) == bool, assert_errors(self, cm.error.assert_lee_filter)
        assert type(self.param.optional.window_size) == int, assert_errors(self, cm.error.assert_window_size)
        assert self.param.optional.window_size % 2 == 1, assert_errors(self, cm.error.assert_widown_size_odd)
        assert self.param.optional.contiguity in ['rook', 'queen'], assert_errors(self, cm.error.assert_contiguity)
        assert self.param.optional.sm_interpolation in ['nearest', 'average', 'cubic'], assert_errors(self, cm.error.assert_sm)
        assert type(self.param.optional.forest_threshold) == float or type(self.param.optional.forest_threshold) == int, assert_errors(self, cm.error.assert_forest_thr)
        assert type(self.param.optional.area_threshold) == float or type(self.param.optional.area_threshold) == int, assert_errors(self, cm.error.assert_area_thr)        
        assert self.param.required.year_1 <= self.param.required.year_2, assert_errors(self, cm.error.y1_lt_y2)

    def _load_tile(self, year):

        try:
            tile = biota.LoadTile(str(self.param.data_dir), 
                                       round_(self.param.required.lat, self.param.required.grid), 
                                       round_(self.param.required.lon, self.param.required.grid), 
                                       year,
                                       parameter_file = self.param.PARAMETER_FILE,
                                       lee_filter = self.param.optional.lee_filter, 
                                       forest_threshold = self.param.optional.forest_threshold, 
                                       area_threshold = self.param.optional.area_threshold, 
                                       output_dir = str(self.param.output_dir))
            return tile
        
        except Exception as e:
            
            self.w_alert.add_msg(f'{e}', type_='error')
            raise
    
    def _process(self):
        """Event trigger when btn_process is clicked
        
        * This function is decorated by loading
        
        """
        
        # Raise error if validation doesn't pass
        self._validate_inputs()
        
        # Create tiles if years are selected.
        if self.param.required.year_1 : self.tile_1 = self._load_tile(int(self.param.required.year_1))
        if self.param.required.year_2 : self.tile_2 = self._load_tile(int(self.param.required.year_2))
                
        for process in self.true_cb:
            self.w_alert.reset()
            if process == 'Gamma0':
                self.w_alert.type_='info'
                self.w_alert.append_msg(cm.outputs.computing.format(process))
                self.gamma0_tile = self.tile_1.getGamma0(polarisation = self.param.optional.polarisation, units = 'decibels')
                self.w_alert.append_msg(cm.outputs.ready.format(process))
                self.w_alert.type_='success'

            elif process == 'Biomass':
                self.w_alert.append_msg(cm.outputs.computing.format(process))
                self.w_alert.type_='info'
                self.agb_tile = self.tile_1.getAGB()
                self.w_alert.append_msg(cm.outputs.ready.format(process))

            elif process in ['Biomass change', 'Change type']:

                self.w_alert.add_msg(cm.outputs.retrieving_ch)
                assert all((self.param.required.year_1 , self.param.required.year_2)), assert_errors(self, cm.error.both_years)
                # Compute change tile
                self.change_tile = biota.LoadChange(
                    self.tile_1, 
                    self.tile_2,
                    change_area_threshold = self.param.optional.change_area_threshold, 
                    change_magnitude_threshold = self.param.optional.change_magnitude_threshold,
                    contiguity = self.param.optional.contiguity
                )
                
                self.w_alert.add_msg(cm.outputs.computing.format(process))
                self.w_alert.type_='info'
                
                if process == 'Biomass change':
                    self.biomass_change_tile = self.change_tile.getAGBChange()

                elif process == 'Change type':
                    self.change_tile.getChangeType()
                    self.forest_change_code = self.change_tile.ChangeCode
                    
                self.w_alert.append_msg(cm.outputs.ready.format(process))
                self.w_alert.type='success'
            else:
                self.w_alert.append_msg(cm.error.at_least_process)
                        
    def _write_raster(self):
        """Write processed raster
        
        * This function is decorated by loading
        
        Args:
            widget (ipywidgets): w_select_output with list of possible processed rasters (self.TILES)
                                
        """
                
        TILES = {
            # Add new tiles when are avaiable
            'Gamma0': self.gamma0_tile,
            'Biomass': self.agb_tile,
            'Biomass change': self.biomass_change_tile,
            'Change type': self.forest_change_code
        }
        
        # Get current raster tile name
        tile_name = self.w_select_output.v_model
        
        # Get tile from selected dropdown
        tile = TILES[tile_name]
        assert (tile is not None), assert_errors(self, cm.error.before_write.format(tile_name))
        
        if tile_name in ['Biomass', 'Gamma0', 'Biomass change']:
            self.tile_1._LoadTile__outputGeoTiff(tile, tile_name)

        elif tile_name in ['Change type']:
            self.tile_1._LoadTile__outputGeoTiff(tile, tile_name, dtype = gdal.GDT_Byte)

        self.w_alert.add_msg(cm.alert.success_export.format(tile_name, self.param.output_dir), type_='success')

        
    def _display(self):
        """Display processed raster.
        
        * This function is decorated by loading
        
        Args:
            widget (ipywidgets): w_select_output with list of possible processed rasters (self.TILES)
                                
        """
        TILES = {
            # Add new tiles when are avaiable
            'Gamma0': self.gamma0_tile,
            'Biomass': self.agb_tile,
            'Biomass change': self.biomass_change_tile,
            'Change type': self.forest_change_code
        }
                
        # Get current raster tile name
        tile_name = self.w_select_output.v_model
        
        # Get tile from selected dropdown
        tile = TILES[tile_name]
        assert (tile is not None), assert_errors(self, cm.error.before_display.format(tile_name))
        
        with self.ou_display:
            self.ou_display.clear_output()
            if tile_name == 'Biomass':
                title, cbartitle, vmin, vmax, cmap = 'AGB', 'tC/ha', 0, 40, 'YlGn'
            elif tile_name == 'Gamma0':
                title, cbartitle, vmin, vmax, cmap = f'Gamma0 {self.param.optional.polarisation}', \
                                                    'decibels', -20, -10, 'Greys_r'
            elif tile_name == 'Biomass change':
                title, cbartitle, vmin, vmax, cmap = 'AGB Change', 'tC/ha', -10, 10, 'YlGn'
            
            elif tile_name == 'Change type':
                # Hide minor gain, minor loss and nonforest in display output
                change_code_display = np.ma.array(
                    tile, 
                    mask = np.zeros_like(tile, dtype = np.bool)
                )
                change_code_display.mask[np.isin(change_code_display, [0, 3, 4, 255])] = True
                
                # Overwrite current tile with new change_code_display
                tile, title, cbartitle, vmin, vmax, cmap = change_code_display, 'Change type', 'Type', 1, 6, 'Spectral'

            # Show arrays with showArray method from LoadTile object
            # We are just using this method to display any tile with the given UI.lat and UI.lon
            self.tile_1._LoadTile__showArray(tile, title, cbartitle, vmin, vmax, cmap)
            self.out_dialog.v_model=True