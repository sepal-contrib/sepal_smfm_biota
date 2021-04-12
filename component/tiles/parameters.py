from biota import download as dw
from pathlib import Path
import os
from datetime import datetime 

from ipywidgets import Output
import ipyvuetify as v

from traitlets import (
    Bool, CInt, CFloat, Unicode, link,
    observe, List, Float, Int
)
from sepal_ui import sepalwidgets as sw

from ..message import cm
from ..scripts.scripts import *
from ..widget.custom_widgets import *


class Optional(v.Card):
    
    lee_filter = Bool(True).tag(sync=True)
    speckle_filter = Bool(True).tag(sync=True)
    
    downsample_factor = CInt(1).tag(sync=True)
    window_size = CInt(5).tag(sync=True)
    forest_threshold = CFloat(10.).tag(sync=True)
    area_threshold = CFloat(0.).tag(sync=True)
    
    change_area_threshold = CInt(2).tag(sync=True)
    change_magnitude_threshold = CInt(15).tag(sync=True)
    
    contiguity = Unicode('queen').tag(sync=True)
    sm_interpolation = Unicode('average').tag(sync=True)
    polarisation = Unicode('HV').tag(sync=True)
    
    
    def __init__(self, **kwargs):
    
        super().__init__(**kwargs)
        
        w_lee_filter = v.Checkbox(label=cm.param.opt.lee_filter, v_model=self.lee_filter)
        w_speckle_filter = v.Checkbox(label=cm.param.opt.speckle_filter, v_model=self.speckle_filter)
        
        w_downsample_factor = v.TextField(label=cm.param.opt.downsample_factor, type='number', v_model=self.downsample_factor)
        w_window_size = v.TextField(label=cm.param.opt.window_size, type='number', v_model=self.window_size)
        w_forest_threshold = v.TextField(label=cm.param.opt.forest_threshold, type='number', v_model=self.forest_threshold)
        w_area_threshold = v.TextField(label=cm.param.opt.area_threshold, type='number', v_model=self.area_threshold)
        
        w_change_area_threshold = v.TextField(label=cm.param.opt.change_area_threshold, type='number', v_model=self.change_area_threshold)
        w_change_magnitude_threshold = v.TextField(label=cm.param.opt.change_magnitude_threshold, type='number', v_model=self.change_magnitude_threshold)
        
        w_contiguity = v.Select(label=cm.param.opt.contiguity, items=['rook', 'queen'], v_model=self.contiguity)
        w_sm_interpolation = v.Select(label=cm.param.opt.sm_interpolation, items=['nearest', 'average', 'cubic'], v_model=self.sm_interpolation)
        w_polarisation = v.Select(label=cm.param.opt.polarisation, items=['HV', 'HH', 'VV', 'VH'], v_model=self.polarisation)

        
        link((w_lee_filter, 'v_model'),(self, 'lee_filter'))
        link((w_speckle_filter, 'v_model'),(self, 'speckle_filter'))
        
        link((w_downsample_factor, 'v_model'),(self, 'downsample_factor'))
        link((w_window_size, 'v_model'),(self, 'window_size'))
        link((w_forest_threshold, 'v_model'),(self, 'forest_threshold'))
        link((w_area_threshold, 'v_model'),(self, 'area_threshold'))
        
        link((w_change_area_threshold, 'v_model'),(self, 'change_area_threshold'))
        link((w_change_magnitude_threshold, 'v_model'),(self, 'change_magnitude_threshold'))
        
        link((w_contiguity, 'v_model'),(self, 'contiguity'))
        link((w_sm_interpolation, 'v_model'),(self, 'sm_interpolation'))
        link((w_polarisation, 'v_model'),(self, 'polarisation'))
        
        self.children=[
            w_lee_filter,
            w_speckle_filter,
            w_downsample_factor,
            w_window_size,
            w_forest_threshold,
            w_area_threshold,
            w_change_area_threshold,
            w_change_magnitude_threshold,
            w_contiguity,
            w_polarisation,
            w_sm_interpolation,
        ]
        
class Required(v.Card):

    # Initial widgets
    lat = Float(0).tag(sync=True)
    lon = Float(-75).tag(sync=True)
    year_1 = Unicode('2016').tag(sync=True)
    year_2 = Unicode('2017').tag(sync=True)
    large_tile = Bool(True).tag(sync=True)
    grid = Int(5).tag(sync=True)
    
    def __init__(self, **kwargs):
    
        super().__init__(**kwargs)
    
        # 1. .Input widgets (Parameters)
        w_lat = v.TextField(disabled=True, label=cm.param.req.latitude,v_model=self.lat,)
        w_lon = v.TextField(disabled=True, label=cm.param.req.longitude, v_model=self.lon,)
        
        w_lat_tooltip = Tooltip(w_lat, cm.tooltip.coordinates)
        w_lon_tooltip = Tooltip(w_lon, cm.tooltip.coordinates)
        
        # Valid years for selection
        valid_years = [str(y) for y in list(range(2007,2010+1))+list(range(2015, datetime.now().year+1))]
        
        w_year_1 = v.Select(label=cm.param.req.year1, items=valid_years, type='number', v_model=self.year_1)
        w_year_2 = v.Select(label=cm.param.req.year2, items=valid_years, type='number',v_model=self.year_2)
        
        w_lg_tile = v.Checkbox(label=cm.param.req.largetile, v_model=self.large_tile)
        w_grid = v.RadioGroup(v_model=self.grid,children=[
            v.Radio(label=cm.param.req._1grid, value=1),
            v.Radio(label=cm.param.req._5grid, value=5)
        ])
        
        self.w_download = sw.Btn(cm.param.req.download, class_='pl-5')
        
        link((w_lon, 'v_model'), (self, 'lon'))
        link((w_lat, 'v_model'), (self, 'lat'))
        link((w_year_1, 'v_model'), (self, 'year_1'))
        link((w_year_2, 'v_model'), (self, 'year_2'))
        link((w_lg_tile, 'v_model'), (self, 'large_tile'))
        link((w_grid, 'v_model'), (self, 'grid'))
        
        self.children=[
                v.CardText(children=[cm.param.req.description]),
                w_lon_tooltip, 
                w_lat_tooltip,
                w_year_1,
                w_year_2,
                w_lg_tile,
                w_grid,
                self.w_download
        ]

class Parameters(v.Layout):
    
    def __init__(self, map_=None, **kwargs):
        
        # Widget classes
        self.class_ = "flex-column pa-2"
        self.row = True
        self.xs12 = True

        super().__init__(**kwargs)
        
        # Parameters
        
        self.map_ = map_
        
        # Set-up workspace
        self._workspace()
        self.PARAMETER_FILE = os.path.join(os.getcwd(), 'biota/cfg/McNicol2018.csv')
        
        # Set up process parameters
        self.required = Required(class_='pa-4')
        self.optional = Optional(class_='pa-4')
        
        # Alerts
        self.w_alert = Alert(children=[cm.param.sel_param]).show()
        self.ou_progress = Output()

        # Events
        self.required.w_download.on_event('click', self._download_event)

        self.children = [
            
            v.Card(children=[
                v.CardTitle(children=[cm.process.header_title]), 
                v.CardText(children=[cm.process.header_text])
            ]),
            
            v.Row(class_="d-flex flex-row ", xs12=True, md6=True,
               children=[
                    v.Col(children=[
                        Tabs(['Required inputs', 'Optional inputs'],
                             [self.required, self.optional])
                    ]),
                    v.Col(
                        children=[
                            v.Card(class_='pa-2 justify-center', children=[
                                map_
                            ])
                        ]
                    ),
            ]),
            v.Card(class_="flex-row pa-2 mb-3", children=[
                self.w_alert,
            ]),
        ]
        
        # Decorate self._download() method
        self._download = loading(self.required.w_download, self.w_alert)(self._download)
        
    def _workspace(self):
        """ Creates the workspace necessary to store the data

        return:
            Returns environment Paths

        """

        base_dir = Path('~').expanduser()

        root_dir = base_dir/'module_results/smfm'
        data_dir = root_dir/'data'
        output_dir = root_dir/'outputs'

        root_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        self.root_dir = root_dir
        self.data_dir  = data_dir
        self.output_dir = output_dir

    def _download_event(self, *args):
        
        years = [int(year) for year in [self.required.year_1, self.required.year_2] if year]
        lat = round_(self.required.lat, self.required.grid)
        lon = round_(self.required.lon, self.required.grid)
        assert (years != []), assert_errors(self, cm.error.at_least_year)
        
        for y in years:
            try:
                self._download(lat, lon, y)
            except:
                pass
            
    def _download(self, *args):
        
        lat, lon, y = args
        self.w_alert.add_msg(cm.alert.downloading.format(y,lat,lon), type_='info')
        dw.download(lat,lon,y,
                    large_tile=self.required.large_tile, 
                    output_dir=self.data_dir, 
                    verbose=True)
        self.w_alert.add_msg(cm.alert.decompressing.format(y), type_='info')
        self._decompress()
        
        self.w_alert.add_msg(cm.alert.done_down.format(y, lat, lon), type_='info')

    def _decompress(self):
        
        tar_files = list(self.data_dir.glob('*.tar.gz'))

        for tar in tar_files:
            if not os.path.exists(os.path.join(self.data_dir, tar.name[:-7])):
                self.w_alert.add_msg(cm.alert.decompressingtar.format(tar.name), type_='info')
                dw.decompress(str(tar))
                self.w_alert.add_msg(cm.alert.done_unzip, type_='success')