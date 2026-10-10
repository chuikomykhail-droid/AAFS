import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

def build_masks(df: pd.DataFrame, units_info: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Builds the 'uncertain status' mask for alerts longer than 24h, 
    exactly 1h with >3h gap, and beyond data_end.
    """
    df = df.copy()
    
    # Filter scope matching units_info
    valid_raions = set(units_info['raion'])
    df['loc_key'] = df['raion'].fillna(df['oblast'])
    df = df[df['loc_key'].isin(valid_raions)].copy()
    
    # Map to unit_id
    loc_to_unit = dict(zip(units_info['raion'], units_info['unit_id']))
    df['unit_id'] = df['loc_key'].map(loc_to_unit)
    
    df = df.sort_values(['unit_id', 'started_at'])
    df['next_start'] = df.groupby('unit_id')['started_at'].shift(-1)
    
    long_thresh = config['thresholds']['long_alert_hours'] * 3600
    
    masks = []
    
    # Rule a: > 24 hours
    rule_a = df[df['duration'] > long_thresh]
    for _, row in rule_a.iterrows():
        masks.append({
            'unit_id': row['unit_id'],
            'start': row['started_at'],
            'end': row['finished_at'],
            'reason': '>24h'
        })
        
    # Rule b: exactly 3600s and next start > 3h away
    rule_b = df[(df['duration'] == 3600) & 
                (df['next_start'].notnull()) & 
                ((df['next_start'] - df['started_at']).dt.total_seconds() > 3 * 3600)]
    for _, row in rule_b.iterrows():
        masks.append({
            'unit_id': row['unit_id'],
            'start': row['started_at'],
            'end': row['next_start'],
            'reason': 'fake_1h'
        })
        
    mask_df = pd.DataFrame(masks)
    
    # Global rule c: after data_end
    # We will add one global mask for each unique unit_id
    data_end = pd.to_datetime(config['data_end'])
    # Using a far future date for end
    future_end = pd.to_datetime("2099-01-01T00:00:00Z")
    
    global_masks = []
    for uid in units_info['unit_id'].unique():
        global_masks.append({
            'unit_id': uid,
            'start': data_end,
            'end': future_end,
            'reason': 'after_data_end'
        })
        
    if not mask_df.empty:
        mask_df = pd.concat([mask_df, pd.DataFrame(global_masks)], ignore_index=True)
    else:
        mask_df = pd.DataFrame(global_masks)
        
    mask_df = mask_df.sort_values(['unit_id', 'start']).reset_index(drop=True)
    
    os.makedirs('data', exist_ok=True)
    mask_df.to_csv('data/mask.csv', index=False)
    logger.info("Saved data/mask.csv")
    
    return mask_df

