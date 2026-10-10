import os
import sys
import yaml
import logging
import pandas as pd
import matplotlib.pyplot as plt

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from alerts.ingest.vadimkin import load_official
from alerts.units import build_units
from alerts.mask import build_masks

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_stage1():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
    os.makedirs('reports/figures', exist_ok=True)
    
    # 1. Load Data
    path = config['dataset']['path']
    sha256 = config['dataset']['sha256']
    df = load_official(path, sha256)
    
    # Raw stats for report
    df_raw = pd.read_csv(path)
    total_raw = len(df_raw)
    total_dedup = len(df_raw.drop_duplicates())
    total_cleaned = len(df)
    
    # 2. Units
    units_info = build_units(df, config)
    
    # 3. Masks
    mask_df, mask_stats = build_masks(df, units_info, config)
    
    # 4. Generate Reports and Plots
    work_start = pd.to_datetime(config['periods']['work_start'])
    data_end = pd.to_datetime(config['data_end'])
    
    df_work = df[(df['started_at'] >= work_start) & (df['started_at'] <= data_end)].copy()
    
    exc = config['excluded_oblasts']
    df_raions = df_work[(df_work['level'] == 'raion') & (~df_work['oblast'].isin(exc))].copy()
    df_kyiv = df_work[(df_work['level'] == 'oblast') & (df_work['oblast'] == 'Kyiv City')].copy()
    df_scope = pd.concat([df_raions, df_kyiv])
    df_scope['loc_key'] = df_scope['raion'].fillna(df_scope['oblast'])
    
    # Numbers for summary
    total_scope = len(df_scope)
    
    # Overlaps in scope
    df_scope = df_scope.sort_values(['loc_key', 'started_at'])
    df_scope['prev_finished'] = df_scope.groupby('loc_key')['finished_at'].shift(1)
    df_scope['is_overlap'] = df_scope['started_at'] < df_scope['prev_finished']
    overlaps = int(df_scope['is_overlap'].sum())
    
    with open('reports/stage1_summary.md', 'w', encoding='utf-8') as f:
        f.write("# Stage 1 Summary\n\n")
        f.write(f"- Total rows raw: {total_raw}\n")
        f.write(f"- After deduplication: {total_dedup}\n")
        f.write(f"- After dropping duration <= 0: {total_cleaned}\n")
        f.write(f"- Active units before merge: {len(units_info)}\n")
        f.write(f"- Active units after merge: {units_info['unit_id'].nunique()}\n")
        f.write(f"- Records in scope (working period): {total_scope}\n")
        f.write(f"- Overlaps after deduplication: {overlaps}\n")
        
        # Mask stats
        f.write(f"\n## Mask Stats\n")
        orig_total = mask_stats['rule_a_loc_total'] + mask_stats['rule_b_loc_total']
        orig_test = mask_stats['rule_a_loc_test'] + mask_stats['rule_b_loc_test']
        unit_total = mask_stats['rule_a_unit_total'] + mask_stats['rule_b_unit_total']
        unit_test = mask_stats['rule_a_unit_test'] + mask_stats['rule_b_unit_test']
        f.write(f"- Masks rule A/B original locs: {orig_total}\n")
        f.write(f"- Masks rule A/B original locs in test: {orig_test}\n")
        f.write(f"- Masks rule A/B merged units: {unit_total}\n")
        f.write(f"- Masks rule A/B merged units in test: {unit_test}\n")
        
        f.write(f"\n## Masked Unit-Hours (by period)\n")
        f.write(f"- Train: {mask_stats.get('train_masked_pct', 0):.2f}%\n")
        f.write(f"- Val: {mask_stats.get('val_masked_pct', 0):.2f}%\n")
        f.write(f"- Test: {mask_stats.get('test_masked_pct', 0):.2f}%\n")

    # If test mask % > 5%, log a warning
    test_pct = mask_stats.get('test_masked_pct', 0)
    if test_pct > 5.0:
        logging.error(f"Test masked percentage is {test_pct:.2f}% (> 5%)!")

    # Plots
    # 1. Level transition
    df_all = df.copy()
    df_all['year_month'] = df_all['started_at'].dt.to_period('M').astype(str)
    monthly = df_all.groupby(['year_month', 'level']).size().unstack(fill_value=0)
    monthly.plot.bar(stacked=True, figsize=(12, 6))
    plt.title("Level distribution by month")
    plt.tight_layout()
    plt.savefig('reports/figures/level_transition.png')
    plt.close()
    
    # 2. Alerts per unit
    counts = df_scope['loc_key'].value_counts()
    counts.plot.hist(bins=30, figsize=(10, 5))
    plt.title("Alerts per unit")
    plt.savefig('reports/figures/alerts_per_unit.png')
    plt.close()
    
    # 3. Duration distribution
    durations = df_scope['duration'] / 3600
    durations[durations < 24].plot.hist(bins=50, logy=True, figsize=(10, 5))
    plt.axvline(24, color='r', linestyle='--')
    plt.title("Duration distribution (hours, log scale)")
    plt.savefig('reports/figures/durations.png')
    plt.close()
    
    # 4. Jaccard distribution
    if os.path.exists('reports/high_sim_pairs.csv'):
        sim_df = pd.read_csv('reports/high_sim_pairs.csv')
        sim_df['jaccard'].plot.hist(bins=20, figsize=(10, 5))
        plt.axvline(config['thresholds']['clone_jaccard'], color='r', linestyle='--')
        plt.title("Jaccard similarity distribution (>= 0.95)")
        plt.savefig('reports/figures/jaccard.png')
        plt.close()

    logging.info("Stage 1 report generated.")

if __name__ == '__main__':
    run_stage1()

