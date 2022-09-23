import inspect
import biota
from pathlib import Path

# Parameter file
biota_root = Path(inspect.getabsfile(biota)).parent
parameter_file = biota_root/"cfg/McNicol2018.csv"