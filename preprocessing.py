import pandas as pd
import numpy as np
import logging

# Configure Logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Standard Schema Mapping
COLUMN_MAP = {
    "impressions": ["impressions", "reach", "views", "total_reach"],
    "likes": ["likes", "favorites", "hearts"],
    "comments": ["comments", "replies", "responses"],
    "shares": ["shares", "retweets", "reposts"],
    "saves": ["saves", "bookmarks"],
    "date": ["date", "post_date", "created_at", "timestamp"],
    "post_type": ["post_type", "format", "media_type"],
    "category": ["category", "topic", "niche"],
    "traffic_source": ["traffic_source", "source", "referral"],
    "followers_gained": ["followers_gained", "new_followers", "growth"],
    "cta": ["cta", "contains_cta", "button"],
    "caption_length": ["caption_length", "text_length", "chars"],
    "hashtags": ["hashtags", "tag_count", "tags"]
}

REQUIRED_COLUMNS = ["date", "likes", "comments", "impressions"]

def map_columns(df):
    """
    Standardizes column names based on flexible mapping.
    Converts all names to lowercase and matches closest mapping.
    """
    try:
        df_clean = df.copy()
        # Convert all current columns to lowercase for matching
        df_clean.columns = [col.lower() for col in df_clean.columns]
        
        rename_dict = {}
        for standard_name, aliases in COLUMN_MAP.items():
            for alias in aliases:
                if alias.lower() in df_clean.columns:
                    rename_dict[alias.lower()] = standard_name
                    break # Stop at first match for this standard name
        
        df_clean = df_clean.rename(columns=rename_dict)
        
        # Check for missing required columns
        missing = [col for col in REQUIRED_COLUMNS if col not in df_clean.columns]
        if missing:
            logger.warning(f"Missing critical columns: {missing}. Dashboard might have empty states.")
            
        return df_clean
    except Exception as e:
        logger.error(f"Error in map_columns: {e}")
        return None

def standardize_types(df):
    """
    Standardizes data types: dates to datetime, numbers to numeric.
    Fills NaNs with defaults: 0 for numeric, 'Unknown' for objects.
    """
    if df is None: return None
    
    try:
        df_clean = df.copy()
        
        # 1. Standardize Date
        if 'date' in df_clean.columns:
            df_clean['date'] = pd.to_datetime(df_clean['date'], errors="coerce")
            
            # Derive 'day' and 'hour' if missing for dashboard compatibility
            if 'day' not in df_clean.columns:
                df_clean['day'] = df_clean['date'].dt.day_name()
            if 'hour' not in df_clean.columns:
                df_clean['hour'] = df_clean['date'].dt.hour
            
        # 2. Standardize Numeric Columns
        numeric_cols = ['likes', 'comments', 'shares', 'saves', 'impressions', 'followers_gained']
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0)
                
        # 3. Fill Categorical NaNs
        categorical_cols = df_clean.select_dtypes(include=['object']).columns
        df_clean[categorical_cols] = df_clean[categorical_cols].fillna("Unknown")
        
        return df_clean
    except Exception as e:
        logger.error(f"Error in standardize_types: {e}")
        return None

def handle_outliers(df):
    """
    Caps extreme values using the Interquartile Range (IQR) method.
    Prevents visualization skewing from outlier posts.
    """
    if df is None: return None
    
    try:
        df_clean = df.copy()
        numeric_cols = ['likes', 'comments', 'shares', 'saves', 'impressions']
        
        for col in numeric_cols:
            if col in df_clean.columns and df_clean[col].dtype in [np.float64, np.int64]:
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Clip values to bounds
                df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
                
        return df_clean
    except Exception as e:
        logger.error(f"Error in handle_outliers: {e}")
        return None

def add_safe_metrics(df):
    """
    Computes engagement metrics with safety checks for zero-division.
    """
    if df is None: return None
    
    try:
        df_clean = df.copy()
        
        # Total Engagement
        cols_to_sum = [c for c in ['likes', 'comments', 'shares', 'saves'] if c in df_clean.columns]
        df_clean['total_engagement'] = df_clean[cols_to_sum].sum(axis=1)
        
        # Raw Engagement Score (Weighted)
        df_clean['engagement_score'] = (
            df_clean.get('likes', 0) + 
            (2 * df_clean.get('comments', 0)) + 
            (3 * df_clean.get('shares', 0)) + 
            (4 * df_clean.get('saves', 0))
        )
        
        # Engagement Rate (Safe Divide)
        if 'impressions' in df_clean.columns:
            df_clean['engagement_rate'] = np.where(
                df_clean['impressions'] > 0,
                df_clean['total_engagement'] / df_clean['impressions'],
                0
            )
        else:
            df_clean['engagement_rate'] = 0.0
            
        return df_clean
    except Exception as e:
        logger.error(f"Error in add_safe_metrics: {e}")
        return None

def validate_sample(df):
    """
    Checks if dataset is large enough for meaningful analysis.
    """
    if df is None or len(df) < 5:
        logger.warning("Dataset too small (less than 5 rows). Results may not be statistically significant.")
        return False
    return True

def dynamic_bins(series, q=4):
    """
    Creates dynamic bins using quantiles instead of hardcoded ranges.
    """
    try:
        return pd.qcut(series, q=q, duplicates='drop')
    except Exception as e:
        logger.warning(f"Binning failed: {e}")
        return None

def preprocess_data(df):
    """
    Orchestrates the full preprocessing pipeline.
    Ensures safe data transformation for the dashboard.
    """
    if df is None or df.empty:
        logger.error("Empty dataframe provided to pipeline.")
        return None
        
    try:
        # Step 1: Mapping
        df = map_columns(df)
        if df is None: return None
        
        # Step 2: Standardize Types
        df = standardize_types(df)
        if df is None: return None
        
        # Step 3: Outlier Handling
        df = handle_outliers(df)
        if df is None: return None
        
        # Step 4: Feature Calculation
        df = add_safe_metrics(df)
        if df is None: return None
        
        # Validation Check (Non-crashing)
        validate_sample(df)
        
        return df
    except Exception as e:
        logger.critical(f"FATAL: Preprocessing pipeline failed: {e}")
        return None
