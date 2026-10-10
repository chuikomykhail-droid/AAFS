import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

def _merge_intervals(sub_df):
    if sub_df.empty: 
        return sub_df
    sub_df = sub_df.sort_values(['unit_id', 'start'])
    merged = []
    for uid, group in sub_df.groupby('unit_id'):
        curr_start = None
        curr_end = None
        curr_reason = None
        for _, row in group.iterrows():
            if curr_start is None:
                curr_start = row['start']
                curr_end = row['end']
                curr_reason = row['reason']
            else:
                if row['start'] <= curr_end:
                    curr_end = max(curr_end, row['end'])
                else:
                    merged.append({'unit_id': uid, 'start': curr_start, 'end': curr_end, 'reason': curr_reason})
                    curr_start = row['start']
                    curr_end = row['end']
                    curr_reason = row['reason']
        if curr_start is not None:
            merged.append({'unit_id': uid, 'start': curr_start, 'end': curr_end, 'reason': curr_reason})
    return pd.DataFrame(merged)

def build_masks(df: pd.DataFrame, units_info: pd.DataFrame, config: dict):
    """
    Builds the 'uncertain status' mask for alerts longer than 24h, 
    exactly 1h with >3h gap, and beyond data_end.
    Returns: mask_df, stats_dict
    """
    df = df.copy()
    
    # Filter scope matching units_info
    exc = config['excluded_oblasts']
    df_raions = df[(df['level'] == 'raion') & (~df['oblast'].isin(exc))].copy()
    df_kyiv = df[(df['level'] == 'oblast') & (df['oblast'] == 'Kyiv City')].copy()
    df_scope = pd.concat([df_raions, df_kyiv])
    df_scope['loc_key'] = df_scope['raion'].fillna(df_scope['oblast'])
    
    # Needs to be sorted by loc_key and started_at to find next_start
    df_scope = df_scope.sort_values(['loc_key', 'started_at'])
    df_scope['next_start'] = df_scope.groupby('loc_key')['started_at'].shift(-1)
    
    # Rules calculated on original loc_key
    long_thresh = config['thresholds']['long_alert_hours'] * 3600
    
    rule_a_locs = df_scope[df_scope['duration'] > long_thresh].copy()
    rule_b_locs = df_scope[(df_scope['duration'] == 3600) & 
                           (df_scope['next_start'].notnull()) & 
                           ((df_scope['next_start'] - df_scope['started_at']).dt.total_seconds() > 3 * 3600)].copy()
    
    # Identify how many are in the test period
    val_end = pd.to_datetime(config['periods']['val_end'])
    
    stats = {
        'rule_a_loc_total': len(rule_a_locs),
        'rule_a_loc_test': len(rule_a_locs[rule_a_locs['started_at'] >= val_end]),
        'rule_b_loc_total': len(rule_b_locs),
        'rule_b_loc_test': len(rule_b_locs[rule_b_locs['started_at'] >= val_end]),
    }

    # Map to unit_id
    loc_to_unit = dict(zip(units_info['raion'], units_info['unit_id']))
    rule_a_locs['unit_id'] = rule_a_locs['loc_key'].map(loc_to_unit)
    rule_b_locs['unit_id'] = rule_b_locs['loc_key'].map(loc_to_unit)
    
    # Merge intervals properly instead of just drop_duplicates
    masks_a, masks_b = [], []
    for _, row in rule_a_locs.iterrows():
        masks_a.append({'unit_id': row['unit_id'], 'start': row['started_at'], 'end': row['finished_at'], 'reason': '>24h'})
    for _, row in rule_b_locs.iterrows():
        masks_b.append({'unit_id': row['unit_id'], 'start': row['started_at'], 'end': row['next_start'], 'reason': 'fake_1h'})
        
    df_a = pd.DataFrame(masks_a)
    df_b = pd.DataFrame(masks_b)
    
    df_a_merged = _merge_intervals(df_a)
    df_b_merged = _merge_intervals(df_b)
    
    # Combine and merge again to get the absolute non-overlapping mask times
    mask_df = pd.concat([df_a_merged, df_b_merged], ignore_index=True)
    if not mask_df.empty:
        mask_df = _merge_intervals(mask_df)
    
    stats['rule_a_unit_total'] = len(df_a_merged)
    stats['rule_a_unit_test'] = len(df_a_merged[df_a_merged['start'] >= val_end]) if not df_a_merged.empty else 0
    stats['rule_b_unit_total'] = len(df_b_merged)
    stats['rule_b_unit_test'] = len(df_b_merged[df_b_merged['start'] >= val_end]) if not df_b_merged.empty else 0
    
    # Global rule c: after data_end
    data_end = pd.to_datetime(config['data_end'])
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
    
    # Calculate masked unit-hours
    work_start = pd.to_datetime(config['periods']['work_start'])
    train_end = pd.to_datetime(config['periods']['train_end'])
    
    def get_intersection_hours(start, end, p_start, p_end):
        actual_start = max(start, p_start)
        actual_end = min(end, p_end)
        if actual_start < actual_end:
            return (actual_end - actual_start).total_seconds() / 3600.0
        return 0.0

    train_h, val_h, test_h = 0.0, 0.0, 0.0
    for _, row in mask_df[mask_df['reason'] != 'after_data_end'].iterrows():
        train_h += get_intersection_hours(row['start'], row['end'], work_start, train_end)
        val_h += get_intersection_hours(row['start'], row['end'], train_end, val_end)
        test_h += get_intersection_hours(row['start'], row['end'], val_end, data_end)
        
    n_units = len(units_info['unit_id'].unique())
    stats['train_masked_pct'] = (train_h / (n_units * (train_end - work_start).total_seconds() / 3600.0)) * 100
    stats['val_masked_pct'] = (val_h / (n_units * (val_end - train_end).total_seconds() / 3600.0)) * 100
    stats['test_masked_pct'] = (test_h / (n_units * (data_end - val_end).total_seconds() / 3600.0)) * 100
    
    os.makedirs('data', exist_ok=True)
    mask_df.to_csv('data/mask.csv', index=False)
    logger.info("Saved data/mask.csv")
    
    return mask_df, stats

