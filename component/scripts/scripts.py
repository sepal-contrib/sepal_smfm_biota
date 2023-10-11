import functools
import math


def loading(btn, alert):
    """Decorator to execute try/except sentence
    and toggle loading button object.

    Params:
        btn (v.Btn): Button to toggle loading
        alert (sw.Alert): Alert to display errors

    Example:
        class A:

            # ...

            self.process = loading(self.btn, self.alert)(self.process)

        def _process_event(self, widget, event, data):
            self.process()

        def process(self):

            '''This will raise and exception'''
            sleep(3)
            assert 1<0, 'This error will be displayed on the alert widget'
    """

    def decorator_loading(func):
        @functools.wraps(func)
        def wrapper_loading(*args, **kwargs):
            btn.loading = True
            try:
                value = func(*args, **kwargs)
            except Exception as e:
                btn.loading = False
                alert.add_msg(f"{e}", type_="error")
                raise e
            btn.loading = False
            return value

        return wrapper_loading

    return decorator_loading


def remove_layers_if(map_, prop, equals_to, _metadata=False):
    """Remove layers with a given property and value.

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
            if hasattr(layer, "_metadata"):
                if layer._metadata[prop] == equals_to:
                    map_.remove_layer(layer)
    else:
        for layer in map_.layers:
            if hasattr(layer, prop):
                if layer.attribution == equals_to:
                    map_.remove_layer(layer)


def round_(x, grid, ax):

    if ax == "lat":
        return grid * math.ceil(x / grid)
    elif ax == "lon":
        return grid * math.floor(x / grid)


#     return grid * math.floor(x/grid)


def assert_errors(self, error):
    self.w_alert.add_msg(error, type_="error")
    return error
