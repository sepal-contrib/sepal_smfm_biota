import math
import requests
import functools

def remove_layers_if(map_, prop, equals_to, _metadata=False):
    """Remove layers with a given property and value
    
    Args:
    
        map_ (ipyleaflet, geemap, SepalMap): Map with Layers to remove
        prop (str): Property or key (if using _metadata) of Layer
        equals_to (str): Value of property or key (if using _metadata) in Layer
        metadata (Bool): Whether the Layers have _metadata attribute or not
        
    Example:
    
        Adding Markers and removing them by '_metadata' property
        
        marker = Marker(location=(lat, lon))
        
        # As ipyleaflet.Markers doesn't have _metadata property, we could create it
        marker.__setattr__('_metadata', {'type':'manual'})
        
        map_.add_layer(marker)
        
        remove_layers_if(map_, 'type', 'manual', _metadata=True)
        It will remove all Layers with _metadata['type']=='manual'
    """
    if _metadata:
        for layer in map_.layers:
            if hasattr(layer, '_metadata'):
                if layer._metadata[prop]==equals_to: map_.remove_layer(layer)
    else:
        for layer in map_.layers:
            if hasattr(layer, prop):
                if layer.attribution==equals_to: map_.remove_layer(layer)
                    
def round_(x, grid, ax):
    
    if ax == 'lat':
        return  grid * math.ceil(x/grid)
    elif ax == 'lon':
        return grid * math.floor(x/grid)
    
#     return grid * math.floor(x/grid)

def assert_errors(self, error):
    self.w_alert.add_msg(error, type_='error')
    return error

