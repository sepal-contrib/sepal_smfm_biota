from pathlib import Path

base_dir = Path("~").expanduser()

root_dir = base_dir / "module_results/smfm_biota"
data_dir = root_dir / "data"
output_dir = root_dir / "outputs"

root_dir.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)
