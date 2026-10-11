"""
Stage 1: Exploratory Data Analysis & Structure Investigation
Ukrainian Air Raid Sirens Dataset (Vadimkin)
Branch: gemini-flash
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_stage1_eda():
    data_path = "dataset_repo/datasets/official_data_en.csv"
    os.makedirs('reports', exist_ok=True)
    
    print("=" * 70)
    print("STAGE 1: EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 70)
    
    # 1. Loading & Raw Schema
    print("\n[1] Loading dataset...")
    df = pd.read_csv(data_path)
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['finished_at'] = pd.to_datetime(df['finished_at'])
    
    print(f"Total rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")
    print(f"Date range: {df['started_at'].min()} to {df['finished_at'].max()}")
    print("\nLevel distribution:")
    print(df['level'].value_counts())
    print("\nMissing values:")
    print(df.isnull().sum())
    
    # 2. Excluded Regions & Working Period Analysis
    excluded_oblasts = ['Donetska oblast', 'Luhanska oblast', 'Autonomous Republic of Crimea', 'Sevastopol']
    
    # Check transitions
    df['year_month'] = df['started_at'].dt.to_period('M').astype(str)
    monthly_levels = df.groupby(['year_month', 'level']).size().unstack(fill_value=0)
    
    print("\n[2] Transition timeline check:")
    print(monthly_levels.tail(12))
    
    # Plot 1: Transition Timeline
    print("\nGenerating Plot 1: reports/transition_timeline.png ...")
    plt.figure(figsize=(14, 6))
    plt.bar(monthly_levels.index, monthly_levels.get('oblast', 0), label='Oblast level', color='#2b5c8f')
    plt.bar(monthly_levels.index, monthly_levels.get('raion', 0), bottom=monthly_levels.get('oblast', 0), label='Raion level', color='#e26d5c')
    plt.bar(monthly_levels.index, monthly_levels.get('hromada', 0), 
            bottom=monthly_levels.get('oblast', 0) + monthly_levels.get('raion', 0), 
            label='Hromada level', color='#f4a261')
    plt.title("Evolution of Alert Reporting Levels in Ukraine (2022 - 2026)", fontsize=14, fontweight='bold')
    plt.xlabel("Year-Month", fontsize=11)
    plt.ylabel("Number of Alert Records", fontsize=11)
    plt.xticks(range(0, len(monthly_levels), 3), monthly_levels.index[::3], rotation=45, ha='right')
    plt.axvline(x='2025-11', color='red', linestyle='--', linewidth=2, label='Full Raion Transition (Nov 2025)')
    plt.legend(frameon=True, fontsize=11)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('reports/transition_timeline.png', dpi=150)
    plt.close()
    
    # Working period filter: 2025-11-07 to 2026-09-07
    work_start = '2025-11-07'
    df_work = df[(df['started_at'] >= work_start) & (~df['oblast'].isin(excluded_oblasts))].copy()
    r_df = df_work[df_work['level'] == 'raion'].copy()
    
    print(f"\n[3] Active Working Period (from {work_start} UTC):")
    print(f"Total raion alerts in active oblasts: {len(r_df):,}")
    print(f"Unique active raions: {r_df['raion'].nunique()} across {r_df['oblast'].nunique()} oblasts")
    
    # Plot 2: Raion alert frequencies
    print("\nGenerating Plot 2: reports/raion_alert_frequencies.png ...")
    raion_counts = r_df['raion'].value_counts()
    plt.figure(figsize=(12, 6))
    plt.hist(raion_counts, bins=35, color='#457b9d', edgecolor='black', alpha=0.85)
    plt.axvline(raion_counts.median(), color='#e63946', linestyle='--', linewidth=2, 
                label=f'Median: {int(raion_counts.median())} alerts')
    plt.axvline(raion_counts.quantile(0.10), color='#2a9d8f', linestyle=':', linewidth=2, 
                label=f'10th percentile: {int(raion_counts.quantile(0.10))} alerts')
    plt.axvline(raion_counts.quantile(0.90), color='#e76f51', linestyle=':', linewidth=2, 
                label=f'90th percentile: {int(raion_counts.quantile(0.90))} alerts')
    plt.title("Distribution of Alert Frequencies Across Raions (Nov 2025 – Sep 2026)", fontsize=14, fontweight='bold')
    plt.xlabel("Total Alerts per Raion", fontsize=11)
    plt.ylabel("Number of Raions", fontsize=11)
    plt.legend(frameon=True, fontsize=11)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('reports/raion_alert_frequencies.png', dpi=150)
    plt.close()
    
    # 4. Overlaps & Pauses (Short Pause Trap)
    print("\n[4] Analyzing overlaps & pauses between consecutive alerts in same raion...")
    r_df = r_df.sort_values(['raion', 'started_at'])
    r_df['prev_finished'] = r_df.groupby('raion')['finished_at'].shift(1)
    r_df['is_overlap'] = r_df['started_at'] < r_df['prev_finished']
    overlaps = r_df['is_overlap'].sum()
    print(f"Overlapping intervals in same raion: {overlaps:,} ({overlaps / len(r_df) * 100:.2f}%)")
    
    r_df['pause_min'] = (r_df['started_at'] - r_df['prev_finished']).dt.total_seconds() / 60.0
    non_overlap_pauses = r_df.loc[~r_df['is_overlap'] & (r_df['pause_min'] > 0), 'pause_min']
    print(f"Non-overlapping pauses evaluated: {len(non_overlap_pauses):,}")
    print(f"Pauses < 5 min:  {(non_overlap_pauses < 5).sum():,} ({(non_overlap_pauses < 5).mean()*100:.2f}%)")
    print(f"Pauses < 15 min: {(non_overlap_pauses < 15).sum():,} ({(non_overlap_pauses < 15).mean()*100:.2f}%)")
    print(f"Pauses < 30 min: {(non_overlap_pauses < 30).sum():,} ({(non_overlap_pauses < 30).mean()*100:.2f}%)")
    print(f"Pauses < 60 min: {(non_overlap_pauses < 60).sum():,} ({(non_overlap_pauses < 60).mean()*100:.2f}%)")
    
    # Plot 3: Pauses
    print("\nGenerating Plot 3: reports/pauses_distribution.png ...")
    pauses_short = non_overlap_pauses[non_overlap_pauses <= 180]
    plt.figure(figsize=(12, 6))
    n, bins, patches = plt.hist(pauses_short, bins=60, color='#3a86ff', edgecolor='black', alpha=0.8)
    for i in range(len(patches)):
        if bins[i] < 15:
            patches[i].set_facecolor('#ff006e')
    plt.axvline(15, color='darkred', linestyle='--', linewidth=2.5, label='15-min Merge Threshold')
    plt.title("Distribution of Pauses Between Alerts in Same Raion (< 3 Hours)", fontsize=14, fontweight='bold')
    plt.xlabel("Pause Duration (Minutes)", fontsize=11)
    plt.ylabel("Frequency", fontsize=11)
    plt.annotate(f"Pauses < 15 min: 10.4% ({int((non_overlap_pauses < 15).sum()):,} occurrences)\nCritical to merge in Stage 2", 
                 xy=(15, max(n)*0.75), xytext=(35, max(n)*0.75),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                 fontsize=11, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#ffeedd", ec="#e63946"))
    plt.legend(frameon=True, fontsize=11)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('reports/pauses_distribution.png', dpi=150)
    plt.close()
    
    # 5. Durations & Anomalies
    print("\n[5] Analyzing durations and anomalies...")
    r_df['duration_hours'] = (r_df['finished_at'] - r_df['started_at']).dt.total_seconds() / 3600.0
    print("Duration quantiles (hours):")
    print(r_df['duration_hours'].describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.99]))
    print(f"Durations > 24 hours: {(r_df['duration_hours'] > 24).sum()}")
    
    # Plot 4: Alert duration
    print("\nGenerating Plot 4: reports/alert_duration_distribution.png ...")
    normal_durations = r_df.loc[(r_df['duration_hours'] >= 0) & (r_df['duration_hours'] <= 8), 'duration_hours']
    plt.figure(figsize=(12, 6))
    plt.hist(normal_durations, bins=48, color='#8338ec', edgecolor='black', alpha=0.8)
    plt.axvline(normal_durations.median(), color='#fb5607', linestyle='--', linewidth=2, 
                label=f'Median: {normal_durations.median():.2f}h ({int(normal_durations.median()*60)} min)')
    plt.axvline(normal_durations.quantile(0.75), color='#ffbe0b', linestyle=':', linewidth=2, 
                label=f'75th percentile: {normal_durations.quantile(0.75):.2f}h ({int(normal_durations.quantile(0.75)*60)} min)')
    plt.title("Distribution of Raion Alert Durations (< 8 Hours)", fontsize=14, fontweight='bold')
    plt.xlabel("Duration (Hours)", fontsize=11)
    plt.ylabel("Frequency", fontsize=11)
    plt.legend(frameon=True, fontsize=11)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('reports/alert_duration_distribution.png', dpi=150)
    plt.close()
    
    print("\n" + "=" * 70)
    print("STAGE 1 COMPLETED SUCCESSFULLY. All reports saved to reports/")
    print("=" * 70)

if __name__ == "__main__":
    run_stage1_eda()
