import pandas as pd
import numpy as np
from itertools import combinations
import networkx as nx
import os
import logging

logger = logging.getLogger(__name__)

def build_units(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Extracts units (raions + Kyiv), computes Jaccard similarity on the train period,
    merges clones (>= 0.997), and saves the mapping.
    """
    exc = config['excluded_oblasts']
    
    # 1. Filter Scope
    df_raions = df[(df['level'] == 'raion') & (~df['oblast'].isin(exc))].copy()
    df_kyiv = df[(df['level'] == 'oblast') & (df['oblast'] == 'Kyiv City')].copy()
    
    df_scope = pd.concat([df_raions, df_kyiv])
    df_scope['raion'] = df_scope['raion'].fillna(df_scope['oblast'])
    
    units_info = df_scope[['oblast', 'raion']].drop_duplicates().sort_values(['oblast', 'raion']).reset_index(drop=True)
    logger.info(f"Initial unique locations (raions + Kyiv): {len(units_info)}")
    
    # 2. Build 1-minute grid for the train period
    train_start = pd.to_datetime(config['periods']['work_start'])
    train_end = pd.to_datetime(config['periods']['train_end'])
    
    df_train = df_scope[(df_scope['started_at'] < train_end) & (df_scope['finished_at'] > train_start)].copy()
    
    minutes = int((train_end - train_start).total_seconds() // 60)
    grid = np.zeros((len(units_info), minutes), dtype=bool)
    
    unit_to_idx = {row.raion: i for i, row in units_info.iterrows()}
    
    for _, row in df_train.iterrows():
        idx = unit_to_idx[row['raion']]
        start_m = int(max(0, (row['started_at'] - train_start).total_seconds() // 60))
        end_m = int(min(minutes, (row['finished_at'] - train_start).total_seconds() // 60))
        if start_m < end_m:
            grid[idx, start_m:end_m] = True
            
    # 3. Compute Jaccard similarities within oblasts
    G = nx.Graph()
    for _, row in units_info.iterrows():
        G.add_node(row.raion, oblast=row.oblast)
        
    high_sim_pairs = []
    clone_threshold = config['thresholds']['clone_jaccard']
    
    for ob in units_info['oblast'].unique():
        ob_units = units_info[units_info['oblast'] == ob]['raion'].tolist()
        for u1, u2 in combinations(ob_units, 2):
            idx1 = unit_to_idx[u1]
            idx2 = unit_to_idx[u2]
            
            arr1 = grid[idx1]
            arr2 = grid[idx2]
            
            intersection = np.sum(arr1 & arr2)
            union = np.sum(arr1 | arr2)
            
            jaccard = intersection / union if union > 0 else 1.0
            
            if jaccard >= clone_threshold:
                G.add_edge(u1, u2)
            
            if jaccard >= 0.95:
                high_sim_pairs.append({
                    'oblast': ob,
                    'raion1': u1,
                    'raion2': u2,
                    'jaccard': jaccard
                })
                
    # 4. Connected components
    comps = list(nx.connected_components(G))
    logger.info(f"Total merged units (components): {len(comps)}")
    
    unit_id_map = {}
    unit_names = {}
    
    # Sort components by their first element to ensure stable IDs
    comps = sorted([sorted(list(c)) for c in comps], key=lambda x: x[0])
    
    for i, comp in enumerate(comps):
        uid = f"U{i:03d}"
        uname = " + ".join(comp)
        for r in comp:
            unit_id_map[r] = uid
            unit_names[r] = uname
            
    units_info['unit_id'] = units_info['raion'].map(unit_id_map)
    units_info['unit_name'] = units_info['raion'].map(unit_names)
    
    os.makedirs('data', exist_ok=True)
    units_info.to_csv('data/units.csv', index=False)
    logger.info("Saved data/units.csv")
    
    os.makedirs('reports', exist_ok=True)
    pd.DataFrame(high_sim_pairs).sort_values('jaccard', ascending=False).to_csv('reports/high_sim_pairs.csv', index=False)
    logger.info("Saved reports/high_sim_pairs.csv")
    
    return units_info

