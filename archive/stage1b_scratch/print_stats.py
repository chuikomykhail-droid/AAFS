import yaml
import pandas as pd
from src.alerts.mask import build_masks
from src.alerts.ingest.vadimkin import load_official

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

df = load_official(config['dataset']['path'], config['dataset']['sha256'])
units = pd.read_csv('data/units.csv')
_, stats = build_masks(df, units, config)
print(stats)

