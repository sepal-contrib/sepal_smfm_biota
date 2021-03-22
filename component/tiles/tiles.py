import ipyvuetify as v
from traitlets import (
    Bool, CInt, CFloat, Unicode, link,
    observe, List, Float, Int
)
from ..message import cm
from sepal_ui import sepalwidgets as sw

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
    year_1 = Unicode().tag(sync=True)
    year_2 = Unicode().tag(sync=True)
    large_tile = Bool(True).tag(sync=True)
    grid = Int(5).tag(sync=True)
    
    def __init__(self, **kwargs):
    
        super().__init__(**kwargs)
    
        # 1. .Input widgets (Parameters)
        w_lat = v.TextField(disabled=True, label=cm.param.req.latitude,v_model=self.lat,)
        w_lon = v.TextField(disabled=True, label=cm.param.req.longitude, v_model=self.lon,)
        w_year_1 = v.TextField(label=cm.param.req.year1, type='number', v_model=self.year_1)
        w_year_2 = v.TextField(label=cm.param.req.year2, type='number',v_model=self.year_2)
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
                w_lon, 
                w_lat,
                w_year_1,
                w_year_2,
                w_lg_tile,
                w_grid,
                self.w_download
        ]
