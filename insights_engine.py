import pandas as pd
import numpy as np

def generate_insights(df):
    """
    Robust data-driven insights engine. 
    Aggregates performance metrics and returns quantitative findings.
    """
    if df is None or len(df) < 5:
        return ["Not enough data to generate reliable insights"]

    df_copy = df.copy()
    insights = []

    # 1. BEST POST TYPE (Avg Engagement)
    try:
        if 'post_type' in df_copy.columns and 'total_engagement' in df_copy.columns:
            post_perf = df_copy.groupby('post_type')['total_engagement'].mean().round(2)
            if not post_perf.empty:
                best_type = post_perf.idxmax()
                avg_val = post_perf.max()
                insights.append(f"{best_type} have the highest average engagement ({avg_val})")
    except Exception:
        pass

    # 2. BEST DAY (Stable Mean)
    try:
        if 'day' in df_copy.columns and 'total_engagement' in df_copy.columns:
            day_perf = df_copy.groupby('day')['total_engagement'].mean().round(2)
            if not day_perf.empty:
                best_day = day_perf.idxmax()
                avg_day = day_perf.max()
                insights.append(f"{best_day} shows peak engagement with {avg_day} average interactions")
    except Exception:
        pass

    # 3. CTA EFFECTIVENESS (Safe %)
    try:
        if 'cta' in df_copy.columns and 'total_engagement' in df_copy.columns:
            # Standardize CTA to boolean locally
            df_copy['cta_clean'] = df_copy['cta'].astype(str).str.lower().isin(['true', 'yes', '1'])
            cta_groups = df_copy.groupby('cta_clean')['total_engagement'].mean()
            
            if len(cta_groups) == 2:
                with_cta = cta_groups.get(True)
                without_cta = cta_groups.get(False)
                
                if without_cta and without_cta > 0:
                    diff = ((with_cta - without_cta) / without_cta) * 100
                    # Clamp at 300% max as per instruction logic
                    diff = min(300, round(diff, 2))
                    if diff > 0:
                        insights.append(f"Posts with CTA perform {diff}% better than those without")
                    else:
                        insights.append(f"Posts without CTA currently show {abs(diff)}% higher engagement")
    except Exception:
        pass

    # 4. TRAFFIC SOURCE (Mean Based)
    try:
        if 'traffic_source' in df_copy.columns and 'total_engagement' in df_copy.columns:
            traffic_perf = df_copy.groupby('traffic_source')['total_engagement'].mean().round(2)
            if not traffic_perf.empty:
                best_src = traffic_perf.idxmax()
                avg_src = traffic_perf.max()
                insights.append(f"'{best_src}' traffic drives the highest average engagement of {avg_src}")
    except Exception:
        pass

    # 5. HASHTAG OPTIMIZATION (Fixed Binning)
    try:
        if 'hashtags' in df_copy.columns and 'total_engagement' in df_copy.columns:
            # Calculate counts safely
            if df_copy['hashtags'].dtype == object:
                df_copy['h_count'] = df_copy['hashtags'].apply(lambda x: len(str(x).split(',')) if ',' in str(x) else 1)
            else:
                df_copy['h_count'] = df_copy['hashtags'].fillna(1)
            
            # Define bins: [0-5], [6-10], [11-20], [21+]
            bins = [-1, 5, 10, 20, 1000]
            labels = ['0–5', '6–10', '11–20', '21+']
            df_copy['h_bin'] = pd.cut(df_copy['h_count'], bins=bins, labels=labels)
            
            h_perf = df_copy.groupby('h_bin', observed=True)['total_engagement'].mean().round(2)
            if not h_perf.empty:
                best_bin = h_perf.idxmax()
                insights.append(f"Posts with {best_bin} hashtags perform best for engagement")
    except Exception:
        pass

    # 6. FOLLOWER GROWTH DRIVER
    try:
        if 'followers_gained' in df_copy.columns and 'post_type' in df_copy.columns:
            growth = df_copy.groupby('post_type')['followers_gained'].mean().round(2)
            if not growth.empty:
                best_growth = growth.idxmax()
                avg_growth = growth.max()
                insights.append(f"'{best_growth}' posts lead in follower growth (avg: {avg_growth})")
    except Exception:
        pass

    # 7. CONSISTENCY CHECK
    try:
        if 'total_engagement' in df_copy.columns:
            std_dev = df_copy['total_engagement'].std()
            mean_val = df_copy['total_engagement'].mean()
            
            if mean_val > 0:
                variability = (std_dev / mean_val).round(2)
                if variability > 0.7:
                    insights.append(f"Engagement is highly inconsistent (variance factor: {variability})")
                else:
                    insights.append(f"Engagement is relatively stable (variance factor: {variability})")
    except Exception:
        pass

    return insights[:7]  # Ensure max 7 insights
