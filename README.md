# Social Lens - Data Visualization and Analytics Tool

An advanced analytics dashboard built with Python to analyze, visualize, and extract insights from social media engagement data.

# Dataset Source : Kaggle
Dataset Name : Instagram Analytics Dataset
About Dataset :
This dataset contains 29,999 Instagram posts with key performance metrics commonly used for content analytics and growth modeling. It includes engagement counts (likes, comments, shares, saves), exposure metrics (reach, impressions), content metadata (media type, category, caption length, hashtags), account features (account type, follower count), traffic source, posting time features, and a performance label.

The dataset is ideal for:

Engagement prediction Performance classification (low/medium/high/viral) Best posting time analysis Traffic source impact Content strategy & optimization EDA / dashboards

What’s included Post identifiers and timestamp features Engagement metrics: likes, comments, shares, saves Reach & impressions Engagement rate (continuous) Content category & media type Traffic source CTA indicator Performance bucket label

Dataset size Rows: 29,999 Columns: 23 Time span: Nov 2024 – Nov 2025

Notes Some engagement fields contain missing values (NaNs). This reflects realistic analytics exports where certain post types or tracking conditions may omit metrics. Users can either impute missing values or remove incomplete rows depending on their modeling goals.

Link : https://www.kaggle.com/datasets/kundanbedmutha/instagram-analytics-dataset
---

## Features

### 1. Robust Data Standardization
- **Automatic Schema Mapping**: Handles inconsistent column names (e.g., "reach" -> "impressions", "favorites" -> "likes").
- **Outlier Handling**: Automatically caps extreme data spikes using the IQR method to maintain visualization accuracy.
- **Data Type Safety**: Converts strings to datetime objects and ensures numeric columns are properly formatted.
- **Dynamic Feature Recovery**: Automatically derives `day` and `hour` from date strings if they are missing.

### 2. Interactive Dashboard
- **KPI Scorecards**: Instant view of Total Posts, Avg Engagement, Engagement Rate, and Follower Growth.
- **10 Statistical Visualizations**:
    1. **Engagement Over Time (Line Chart)**: Tracks the sum of engagement across dates to spot temporal trends and spikes.
    2. **Daily Engagement Heatmap**: A matrix showing which hours on which days produce the highest average engagement, using color gradients to spot the 'best time to post'.
    3. **Avg Engagement by Post Type (Bar Chart)**: Compares performance averages between Reels, Carousels, Static Posts, etc.
    4. **Engagement Score Distribution (Boxplot)**: Shows the spread (quartiles) of engagement by post type, making it easy to see variance and remaining outliers.
    5. **Hashtag Count vs Score (Scatter & Regression)**: Plots each post based on its hashtag count to reveal if more hashtags yield better engagement. Includes a Pearson correlation line.
    6. **Caption Length vs Score (Scatter & Regression)**: Analyzes if longer text descriptions correlate with higher or lower engagement.
    7. **CTA Comparison (Bar Chart)**: Evaluates the average engagement difference between posts that include a Call-to-Action versus those that don't.
    8. **Engagement by Traffic Source (Bar Chart)**: Identifies which traffic source (e.g., Explore page vs Home feed) generates the most interactions.
    9. **Score Distribution + KDE (Histogram)**: Visualizes the overall frequency of engagement scores across the dataset, smoothed with Kernel Density Estimation (KDE) to show probability shapes.
    10. **Score vs Follower Growth (Scatter)**: Checks the relationship between how viral a post goes (Engagement Score) versus its actual return on audience size (Followers Gained).
- **Seaborn Integration**: Premium, statistically informed plots with regression lines and KDE distributions.

### 3. Smart Filtering
- **Calendar Selection**: Use `tkcalendar` for precise date range filtering.
- **Categorical Filters**: Sift data by Post Type, Category, Traffic Source, and CTA.
- **Instant Refresh**: Dashboard and insights update immediately when filters are applied.

### 4. Data-Driven Insights
- Automated generation of key findings (e.g., "Reels perform 28% better", "Optimal hashtag count is 6–10").

### 5. Professional Reporting
- **Data Export**: Export filtered datasets directly to CSV.
- **Dynamic Chart Exporting**: Automatically exports all 10 dynamically generated, high-resolution dashboard charts to PNG in a single action, accurately reflecting your filtered data.

### 6. Standardized Analytics View
- **Strict Chart Labels**: Every chart enforces standard professional titling ("Metric vs Dimension") alongside rigorous axis labels to maintain context, minimizing misinterpretation during presentations.

---

## 🛠️ Technology Stack & Widgets

### Core Stack
- **GUI Engine**: Python Tkinter
- **Data Processing**: Pandas, NumPy
- **Visuals**: Matplotlib, Seaborn
- **Statistics**: SciPy (Pearson Correlation)

### UI Components & Widgets Used
- **`tkinter.ttk` (Themed Tkinter)**: Used for modern, system-themed widgets replacing standard Tkinter ones (e.g., `ttk.Frame`, `ttk.Label`, `ttk.Button`, `ttk.Combobox`, `ttk.Separator`). We utilized custom styles (e.g., `clam` theme) for a cleaner UI.
- **`tkcalendar.DateEntry`**: Essential for the dynamic date range filtering (Start Date & End Date), providing an interactive dropdown calendar interface.
- **`FigureCanvasTkAgg`**: From `matplotlib.backends.backend_tkagg`, this acts as the bridge widget to embed Matplotlib figures and Seaborn charts directly into Tkinter frame containers seamlessly.
- **`tkinter.Canvas` & `ttk.Scrollbar`**: Used together to create robust scrollable container areas for the dynamically generated charts array and long insight reports.
- **`tkinter.filedialog` & `tkinter.messagebox`**: Built-in modules for handling CSV upload dialog flows and showing user alerts/errors.

---

## Project Structure

project/
├── main.py                 # Core application, UI logic, and control flow
├── preprocessing.py        # Robust data pipeline (mapping, outliers, etc.)
├── insights_engine.py      # Statistical analysis and insight generation logic
├── dva_project_dataset.csv # Sample dataset for analysis
└── README.md               # Project documentation


## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

### 2. Install Dependencies
Run the following command to install the required libraries:
```bash
pip install pandas matplotlib seaborn scipy tkcalendar
```

### 3. Run the App
```bash
python main.py
```

---

## How to Use

1. **Import Data**: Go to the **Upload** page and select your social media CSV file.
2. **Explore Dashboard**: Navigate to **Dashboard** to see the KPI cards and charts.
3. **Refine Results**: Use the top filter bar (Date selectors, dropdowns) and click **Apply Filters**.
4. **Read Findings**: Visit the **Insights** page to see automated data-driven recommendations.
5. **Export Reports**: Go to **Export** to save your filtered dataset or download the dashboard charts as images.

---

## Data Schema Requirements

The analyzer is now flexible and handles multiple column aliases. Minimum requirements:
- `date` (or `created_at`, `post_date`)
- `likes` (or `favorites`)
- `comments` (or `replies`)
- `impressions` (or `views`, `reach`)

The following are automatically standardized if present:
- `shares`, `saves`, `post_type`, `category`, `traffic_source`, `cta`, `hashtags`, `followers_gained`.

*Note: If `day` or `hour` are missing, they are automatically derived from the `date` column.*

---

## DEVELOPED BY : Puru Gupta 
