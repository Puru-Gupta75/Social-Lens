import os
import tkinter as tk
import matplotlib.pyplot as plt
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tkinter import ttk, filedialog, messagebox
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr

from insights_engine import generate_insights
from preprocessing import preprocess_data 

# Visual Styles
sns.set_style("whitegrid")



# Constants for Dataset Validation (Simplified for Robust Matching)
REQUIRED_COLUMNS = [
    'date', 'post_type', 'category', 'traffic_source', 
    'likes', 'comments', 'shares', 'saves', 'impressions'
]

def validate_dataset(df):
    """
    Checks if the dataframe contains standard required columns.
    Note: These should have been mapped in preprocessing.py.
    """
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing_columns

def apply_filters(df, filters_dict):
    """
    Applies filters to the dataframe based on the provided dictionary.
    Returns a new copy of the filtered dataframe.
    """
    if df is None or df.empty:
        return df
        
    filtered_df = df.copy()
    
    # 1. Date Range Filter
    if 'date' in filtered_df.columns:
        filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    
    start_date = filters_dict.get('start_date')
    end_date = filters_dict.get('end_date')
    
    if start_date:
        filtered_df = filtered_df[filtered_df['date'] >= pd.to_datetime(start_date)]
            
    if end_date:
        filtered_df = filtered_df[filtered_df['date'] <= pd.to_datetime(end_date)]
            
    # 2. Categorical Filters
    categorical_map = {
        'post_type': 'post_type',
        'category': 'category',
        'traffic_source': 'traffic_source'
    }
    
    for key, col in categorical_map.items():
        val = filters_dict.get(key)
        if val and val != "All":
            filtered_df = filtered_df[filtered_df[col] == val]
            
    # 3. CTA Filter
    cta_val = filters_dict.get('cta')
    if cta_val == "Yes":
        filtered_df = filtered_df[filtered_df['cta'].astype(str).str.lower().isin(['true', 'yes', '1'])]
    elif cta_val == "No":
        filtered_df = filtered_df[~filtered_df['cta'].astype(str).str.lower().isin(['true', 'yes', '1'])]
        
    # Debug Logs
    print(f"DEBUG: Applied Filters: {filters_dict}")
    print(f"DEBUG: Resulting DF Shape: {filtered_df.shape}")
        
    return filtered_df


def create_chart(parent_frame):
    """
    Creates a matplotlib figure and axes, embeds it in a Tkinter frame.
    Returns (fig, ax, canvas).
    """
    # Create Figure and Axes
    # Standard size/dpi for dashboard integration
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    fig.patch.set_facecolor('#ffffff') # Match white background of content frames
    
    # Embed in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas_widget = canvas.get_tk_widget()
    
    # Ensure chart takes up full space
    canvas_widget.pack(fill="both", expand=True)
    
    # Final layout polish
    fig.tight_layout()
    
    return fig, ax, canvas

class UploadPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title Label
        title = ttk.Label(self, text="Upload Dataset", font=("Segoe UI", 24, "bold"), style="PageTitle.TLabel")
        title.grid(row=0, column=0, sticky="w", padx=40, pady=(40, 10))
        
        # Main Content Frame
        self.content = ttk.Frame(self, style="Content.TFrame")
        self.content.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        
        # Center the button in content
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        
        # Upload Button
        self.upload_btn = ttk.Button(
            self.content, 
            text="Select CSV File", 
            command=self.select_file,
            cursor="hand2"
        )
        self.upload_btn.grid(row=0, column=0, ipady=10, ipadx=20)

    def select_file(self):
        """Triggers file dialog and calls controller to load data."""
        file_path = filedialog.askopenfilename(
            title="Select Social Media Dataset",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.controller.load_dataset(file_path)

class DashboardPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        # Grid layout for the page
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Content area expands
        
        # 1. Page Title
        title = ttk.Label(
            self, 
            text="Dashboard Overview", 
            font=("Segoe UI", 24, "bold"), 
            style="PageTitle.TLabel"
        )
        title.grid(row=0, column=0, sticky="w", padx=40, pady=(40, 10))
        
        # 2. Filter Section (Horizontal Bar)
        self.filter_frame = ttk.Frame(self, style="Content.TFrame", padding=15)
        self.filter_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 15))
        
        # Column setup for equal distribution
        for i in range(7):
            self.filter_frame.grid_columnconfigure(i, weight=1)

        # Filter Labels and Widgets
        # (Using instance variables as requested)
        
        
        # Date Range: Start Date
        ttk.Label(self.filter_frame, text="Start Date", style="FilterLabel.TLabel").grid(row=0, column=0, sticky="w", padx=5)
        self.start_date_picker = DateEntry(self.filter_frame, width=12, background='#4b7bec', 
                                         foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date_picker.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 5))
        
        # Date Range: End Date
        ttk.Label(self.filter_frame, text="End Date", style="FilterLabel.TLabel").grid(row=0, column=1, sticky="w", padx=5)
        self.end_date_picker = DateEntry(self.filter_frame, width=12, background='#4b7bec', 
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date_picker.grid(row=1, column=1, sticky="ew", padx=5, pady=(2, 5))

        
        # Post Type
        ttk.Label(self.filter_frame, text="Post Type", style="FilterLabel.TLabel").grid(row=0, column=2, sticky="w", padx=5)
        self.post_type_dropdown = ttk.Combobox(self.filter_frame, values=["All"], state="readonly")
        self.post_type_dropdown.set("All")
        self.post_type_dropdown.grid(row=1, column=2, sticky="ew", padx=5, pady=(2, 5))
        
        # Category
        ttk.Label(self.filter_frame, text="Category", style="FilterLabel.TLabel").grid(row=0, column=3, sticky="w", padx=5)
        self.category_dropdown = ttk.Combobox(self.filter_frame, values=["All"], state="readonly")
        self.category_dropdown.set("All")
        self.category_dropdown.grid(row=1, column=3, sticky="ew", padx=5, pady=(2, 5))
        
        # Traffic Source
        ttk.Label(self.filter_frame, text="Traffic Source", style="FilterLabel.TLabel").grid(row=0, column=4, sticky="w", padx=5)
        self.traffic_source_dropdown = ttk.Combobox(self.filter_frame, values=["All"], state="readonly")
        self.traffic_source_dropdown.set("All")
        self.traffic_source_dropdown.grid(row=1, column=4, sticky="ew", padx=5, pady=(2, 5))
        
        # CTA (Yes/No)
        ttk.Label(self.filter_frame, text="CTA", style="FilterLabel.TLabel").grid(row=0, column=5, sticky="w", padx=5)
        self.cta_dropdown = ttk.Combobox(self.filter_frame, values=["All", "Yes", "No"], state="readonly")
        self.cta_dropdown.set("All")
        self.cta_dropdown.grid(row=1, column=5, sticky="ew", padx=5, pady=(2, 5))
        
        # Apply Button
        self.apply_btn = ttk.Button(
            self.filter_frame, 
            text="Apply Filters", 
            command=self.on_apply_filters,
            cursor="hand2"
        )
        self.apply_btn.grid(row=1, column=6, sticky="ew", padx=10, pady=(2, 5))
        
        # Reset Button
        self.reset_btn = ttk.Button(
            self.filter_frame, 
            text="Reset Filters", 
            command=self.on_reset_filters,
            cursor="hand2"
        )
        self.reset_btn.grid(row=0, column=6, sticky="ew", padx=10, pady=(5, 2))

        
        # 3. Main Dashboard Content (Scrollable Area)
        self.container = ttk.Frame(self, style="Content.TFrame")
        self.container.grid(row=2, column=0, sticky="nsew", padx=40, pady=0)
        self.grid_rowconfigure(2, weight=1)

        # Canvas + Scrollbar setup
        self.canvas = tk.Canvas(self.container, background="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas, style="Content.TFrame")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Dashboard UI Elements inside scrollable_frame ---
        
        # 1. KPI SECTION
        self.kpi_frame = ttk.Frame(self.scrollable_frame, style="Content.TFrame", padding=(10, 20))
        self.kpi_frame.pack(fill="x")
        
        for i in range(4): self.kpi_frame.grid_columnconfigure(i, weight=1)
        
        # KPI Cards Factory
        def create_kpi(parent, title, row, col):
            f = ttk.Frame(parent, style="Content.TFrame")
            f.grid(row=row, column=col, sticky="nsew")
            ttk.Label(f, text=title, font=("Segoe UI", 10, "bold"), foreground="#666666", background="white").pack()
            lbl = ttk.Label(f, text="0", font=("Segoe UI", 20, "bold"), foreground="#4b7bec", background="white")
            lbl.pack()
            return lbl

        self.kpi_posts = create_kpi(self.kpi_frame, "Total Posts", 0, 0)
        self.kpi_engagement = create_kpi(self.kpi_frame, "Avg Engagement", 0, 1)
        self.kpi_rate = create_kpi(self.kpi_frame, "Avg Eng. Rate", 0, 2)
        self.kpi_followers = create_kpi(self.kpi_frame, "Total Growth", 0, 3)

        # 2. CHARTS GRID
        self.charts_container = ttk.Frame(self.scrollable_frame, style="Content.TFrame")
        self.charts_container.pack(fill="both", expand=True, pady=20)
        
        self._init_charts(self.charts_container)


    def populate_dropdowns(self, df):
        """Populates filter dropdowns and date limits dynamically from the dataset."""
        if df is None: return
        
        # Sync Date Range
        try:
            df['date'] = pd.to_datetime(df['date'])
            min_date = df['date'].min()
            max_date = df['date'].max()
            if not pd.isnull(min_date):
                self.start_date_picker.set_date(min_date)
            if not pd.isnull(max_date):
                self.end_date_picker.set_date(max_date)
        except:
            pass

        # Update Post Type
        types = ["All"] + sorted(df['post_type'].unique().tolist())
        self.post_type_dropdown['values'] = types
        self.post_type_dropdown.set("All")
        
        # Update Category
        cats = ["All"] + sorted(df['category'].unique().tolist())
        self.category_dropdown['values'] = cats
        self.category_dropdown.set("All")
        
        # Update Traffic Source
        sources = ["All"] + sorted(df['traffic_source'].unique().tolist())
        self.traffic_source_dropdown['values'] = sources
        self.traffic_source_dropdown.set("All")

    def on_reset_filters(self):
        """Resets all filters to default and restores working_df."""
        if self.controller.reset_data():
            # Trigger dropdown population which sets date bounds automatically
            self.populate_dropdowns(self.controller.get_processed_data())
            self.cta_dropdown.set("All")
            self.update_charts()
            self.controller.frames[InsightsPage].refresh_insights()
            messagebox.showinfo("Reset", "Filters cleared and data restored.")


    def on_apply_filters(self):
        """Reads UI values and triggers filtering via controller."""
        data = self.controller.get_processed_data()
        if data is None:
            messagebox.showwarning("No Data", "Please upload a dataset first!")
            return

        filters_dict = {
            'start_date': self.start_date_picker.get_date(),
            'end_date': self.end_date_picker.get_date(),
            'post_type': self.post_type_dropdown.get(),
            'category': self.category_dropdown.get(),
            'traffic_source': self.traffic_source_dropdown.get(),
            'cta': self.cta_dropdown.get()
        }


        try:
            filtered_df = apply_filters(data, filters_dict)
            
            if filtered_df.empty:
                messagebox.showinfo("No Matches", "No data matches selected filters.")
                
            self.controller.working_df = filtered_df
            self.update_charts()
            
            # Refresh Insights automatically
            self.controller.frames[InsightsPage].refresh_insights()
            
        except Exception as e:
            messagebox.showerror("Filtering Error", f"Failed to apply filters:\n{str(e)}")


    def _init_charts(self, parent):
        """Initializes all matplotlib figures/axes/canvases in a grid."""
        self.charts = {} # stores (fig, ax, canvas)
        
        # Grid Configuration (2 columns)
        for i in range(2): parent.grid_columnconfigure(i, weight=1)
        
        chart_configs = [
            ("line", "Engagement Over Time", 0, 0),
            ("heatmap", "Daily Engagement Heatmap", 0, 1),
            ("post_type_bar", "Avg Engagement by Post Type", 1, 0),
            ("engagement_boxplot", "Engagement Score Distribution", 1, 1),
            ("hashtags_scatter", "Hashtag Count vs Score", 2, 0),
            ("caption_scatter", "Caption Length vs Score", 2, 1),
            ("cta_bar", "CTA Comparison (Avg)", 3, 0),
            ("traffic_bar", "Engagement by Traffic Source", 3, 1),
            ("engagement_hist", "Score Distribution + KDE", 4, 0),
            ("growth_scatter", "Score vs Follower Growth", 4, 1)
        ]

        for chart_type, title, row, col in chart_configs:
            frame = ttk.Frame(parent, style="Content.TFrame")
            frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            
            fig, ax = plt.subplots(figsize=(5, 3.5), dpi=90)
            fig.patch.set_facecolor('#ffffff')
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self.charts[chart_type] = (fig, ax, canvas)

    def _plot_chart(self, ax, chart_type, df):
        """Central modular plotting logic using seaborn."""
        ax.clear()
        if df is None or df.empty:
            ax.text(0.5, 0.5, "No Data for Selection", ha='center', va='center', color='gray')
            return

        palette = "viridis"
        try:
            if chart_type == "line":
                data = df.groupby('date')['total_engagement'].sum().reset_index()
                sns.lineplot(data=data, x='date', y='total_engagement', ax=ax, color='#4b7bec', marker='o')
                plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
                ax.set_title("Total Engagement Over Time")
                ax.set_xlabel("Date")
                ax.set_ylabel("Total Engagement")

            elif chart_type == "heatmap":
                pivot = df.pivot_table(index='day', columns='hour', values='total_engagement', aggfunc='mean')
                sns.heatmap(pivot, ax=ax, cmap="YlGnBu", cbar=False)
                ax.set_title("Average Engagement by Day and Hour")
                ax.set_xlabel("Hour of Day")
                ax.set_ylabel("Day of Week")

            elif chart_type == "post_type_bar":
                sns.barplot(data=df, x='post_type', y='total_engagement', ax=ax, palette=palette, errorbar=None)
                ax.set_title("Average Engagement by Post Type")
                ax.set_xlabel("Post Type")
                ax.set_ylabel("Avg Engagement")

            elif chart_type == "engagement_boxplot":
                sns.boxplot(data=df, x='post_type', y='engagement_score', ax=ax, palette="Set2")
                ax.set_title("Engagement Distribution by Post Type")
                ax.set_xlabel("Post Type")
                ax.set_ylabel("Engagement")

            elif chart_type == "hashtags_scatter":
                sns.scatterplot(data=df, x='hashtags', y='engagement_score', ax=ax, alpha=0.6)
                sns.regplot(data=df, x='hashtags', y='engagement_score', ax=ax, scatter=False, color='red')
                ax.set_title("Engagement vs Hashtag Count")
                ax.set_xlabel("Hashtag Count")
                ax.set_ylabel("Engagement")

            elif chart_type == "caption_scatter":
                sns.scatterplot(data=df, x='caption_length', y='engagement_score', ax=ax, alpha=0.6)
                sns.regplot(data=df, x='caption_length', y='engagement_score', ax=ax, scatter=False, color='red')
                ax.set_title("Engagement vs Caption Length")
                ax.set_xlabel("Caption Length")
                ax.set_ylabel("Engagement")

            elif chart_type == "cta_bar":
                sns.barplot(data=df, x='cta', y='total_engagement', ax=ax, palette="coolwarm", errorbar=None)
                ax.set_title("Average Engagement: CTA vs No CTA")
                ax.set_xlabel("CTA Presence")
                ax.set_ylabel("Avg Engagement")

            elif chart_type == "traffic_bar":
                sns.barplot(data=df, x='traffic_source', y='total_engagement', ax=ax, palette="magma", errorbar=None)
                ax.set_title("Average Engagement by Traffic Source")
                ax.set_xlabel("Traffic Source")
                ax.set_ylabel("Avg Engagement")

            elif chart_type == "engagement_hist":
                sns.histplot(df['engagement_score'], kde=True, ax=ax, color='#4b7bec')
                ax.set_title("Engagement Score Distribution")
                ax.set_xlabel("Engagement Score")
                ax.set_ylabel("Frequency")

            elif chart_type == "growth_scatter":
                sns.scatterplot(data=df, x='engagement_score', y='followers_gained', ax=ax, alpha=0.5, color='green')
                ax.set_title("Engagement vs Followers Gained")
                ax.set_xlabel("Followers Gained")
                ax.set_ylabel("Engagement")

            ax.tick_params(axis='both', which='major', labelsize=8)
        except Exception as e:
            ax.text(0.5, 0.5, f"Plotting Error", ha='center', va='center', color='red')

    def update_charts(self):
        """Fetches latest data, calculates KPIs, and refreshes dashboard visuals."""
        df = self.controller.get_data()
        
        # 1. Update KPIs
        if df is not None and not df.empty:
            self.kpi_posts.config(text=f"{len(df)}")
            self.kpi_engagement.config(text=f"{df['total_engagement'].mean():.1f}")
            self.kpi_rate.config(text=f"{df['engagement_rate'].mean():.2%}")
            self.kpi_followers.config(text=f"{df['followers_gained'].sum()}")
        else:
            for lbl in [self.kpi_posts, self.kpi_engagement, self.kpi_rate, self.kpi_followers]:
                lbl.config(text="0")

        # 2. Update Charts
        for chart_type, (fig, ax, canvas) in self.charts.items():
            self._plot_chart(ax, chart_type, df)
            fig.tight_layout()
            canvas.draw()


class InsightsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Results area expands
        
        # 1. Page Title
        title = ttk.Label(self, text="Engagement Insights", font=("Segoe UI", 24, "bold"), style="PageTitle.TLabel")
        title.grid(row=0, column=0, sticky="w", padx=40, pady=(40, 10))
        
        # 2. Controls Section
        self.controls = ttk.Frame(self, style="Main.TFrame")
        self.controls.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 10))
        
        self.generate_btn = ttk.Button(
            self.controls, 
            text="Refresh Insights", 
            command=self.refresh_insights,
            cursor="hand2"
        )

        self.generate_btn.pack(side="left")

        # 3. Main Content (Scrollable Container)
        self.container = ttk.Frame(self, style="Content.TFrame")
        self.container.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 40))
        
        # Scrollable Canvas Setup
        self.canvas = tk.Canvas(self.container, background="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        
        # Internal Frame for Labels
        self.scrollable_frame = ttk.Frame(self.canvas, style="Content.TFrame")
        
        # Center the internal frame and handle resizing
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Ensure inner frame fills horizontal space for text wrapping
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_canvas_configure(self, event):
        """Syncs the width of the inner frame and updates label wrapping."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        # Update wraplength for any existing labels
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.configure(wraplength=event.width - 50)

    def refresh_insights(self):
        """Fetches data, runs engine, and renders bulleted list of results."""
        # Get latest filtered data
        df = self.controller.get_data()

        # Clear previous
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if df is None or df.empty:
            msg = ttk.Label(self.scrollable_frame, text="No matches found for selected filters.", 
                            font=("Segoe UI", 12, "italic"), background="white", padding=30)
            msg.pack(anchor="w")
            return

        # Generate and Render
        insights = generate_insights(df)
        for text in insights:
            lbl = ttk.Label(self.scrollable_frame, text=f"• {text}", font=("Segoe UI", 12),
                            wraplength=self.canvas.winfo_width() - 50, justify="left",
                            background="white", padding=(20, 10))
            lbl.pack(fill="x", anchor="w")
            ttk.Separator(self.scrollable_frame, orient="horizontal").pack(fill="x", padx=20)


class ExportPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 1. Page Title
        title = ttk.Label(self, text="Export Reports", font=("Segoe UI", 24, "bold"), style="PageTitle.TLabel")
        title.grid(row=0, column=0, sticky="w", padx=40, pady=(40, 10))
        
        # 2. Main Content Frame
        self.content = ttk.Frame(self, style="Content.TFrame")
        self.content.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        
        # Grid layout for content centering
        self.content.grid_columnconfigure(0, weight=1)
        
        # Instruction Label
        instr = ttk.Label(
            self.content, 
            text="Download current analysis results to your local machine.",
            background="white",
            font=("Segoe UI", 11)
        )
        instr.grid(row=0, column=0, pady=(40, 20))

        # Action Buttons Container
        self.btn_frame = ttk.Frame(self.content, style="Content.TFrame")
        self.btn_frame.grid(row=1, column=0, pady=20)

        # Export CSV Button
        self.export_csv_btn = ttk.Button(
            self.btn_frame, 
            text="Export Filtered Data (CSV)", 
            command=self.export_data_csv,
            cursor="hand2"
        )
        self.export_csv_btn.pack(side="left", padx=10, ipady=5)

        # Export PNG Button
        self.export_png_btn = ttk.Button(
            self.btn_frame, 
            text="Export Dashboard Charts (PNG)", 
            command=self.export_charts_png,
            cursor="hand2"
        )
        self.export_png_btn.pack(side="left", padx=10, ipady=5)

    def export_data_csv(self):
        """Saves the current working_df to a CSV file."""
        df = self.controller.get_data()
        
        if df is None or df.empty:
            messagebox.showwarning("No Data", "No filtered dataset available to export. Please apply filters first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Filtered Data"
        )

        if file_path:
            try:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Export Success", f"Dataset saved successfully to:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save CSV:\n{str(e)}")

    def export_charts_png(self):
        """Saves existing figures from DashboardPage as PNG images in a selected directory."""
        # 1. Locate existing figures from the dashboard via controller
        try:
            dashboard = self.controller.frames[DashboardPage]
            if not getattr(dashboard, 'charts', None):
                raise AttributeError
        except (KeyError, AttributeError):
            messagebox.showerror("Export Error", "Dashboard charts are not currently available.")
            return

        # 2. Select Directory
        dir_path = filedialog.askdirectory(title="Select Folder to Save Charts")
        if not dir_path:
            return

        # 3. Save each figure
        try:
            for chart_type, (fig, ax, canvas) in dashboard.charts.items():
                file_name = f"{chart_type}.png"
                path = os.path.join(dir_path, file_name)
                fig.savefig(path, dpi=300, bbox_inches='tight')
            
            messagebox.showinfo("Export Success", f"Charts exported successfully to:\n{dir_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save images:\n{str(e)}")


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # State Management
        self.raw_df = None
        self.working_df = None
        self.processed_df = None

        # Constants for UI
        self.SIDEBAR_COLOR = "#1e1e2f"
        self.MAIN_BG = "#f5f6fa"
        self.HIGHLIGHT_COLOR = "#2d2d44"
        self.ACTIVE_COLOR = "#4b7bec"
        self.TEXT_COLOR = "#ffffff"

        # Window Config
        self.title("Social Media Engagement Analyzer")
        self.geometry("1200x700")
        self.minsize(1200, 700)
        self.configure(bg=self.MAIN_BG)

        # Initialize Styles
        self._setup_styles()

        # Layout Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (Fixed Width)
        self.sidebar = tk.Frame(self, width=500, bg=self.SIDEBAR_COLOR, relief="flat")
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        # Right Area (Header + Container)
        self.right_container = tk.Frame(self, bg=self.MAIN_BG)
        self.right_container.grid(row=0, column=1, sticky="nsew")
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(1, weight=1)

        # Top Header Bar
        self.header_bar = tk.Frame(self.right_container, height=60, bg="#ffffff", relief="flat")
        self.header_bar.grid(row=0, column=0, sticky="ew")
        self.header_bar.grid_propagate(False)
        
        self.header_label = ttk.Label(
            self.header_bar, 
            text="Social Media Engagement Analyzer", 
            style="Header.TLabel"
        )
        self.header_label.pack(side="left", padx=30, pady=15)

        # Page Container
        self.container = ttk.Frame(self.right_container, style="Main.TFrame")
        self.container.grid(row=1, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.sidebar_buttons = {}

        # Initialize Frames
        for F in (UploadPage, DashboardPage, InsightsPage, ExportPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Setup Sidebar Content
        self._init_sidebar()

        # Initial Frame
        self.show_frame(UploadPage)

    # --- Data State Management Methods ---

    def load_dataset(self, file_path):
        """Loads dataset, validates columns, and initializes raw/working state."""
        try:
            # Load Data
            df = pd.read_csv(file_path)
            
            # --- NEW PREPROCESSING FLOW ---
            processed_df = preprocess_data(df)
            
            if processed_df is None:
                messagebox.showerror("Preprocessing Error", "The dataset could not be standardized or contains fatal errors.")
                return

            # Check for missing columns AFTER mapping attempt
            missing_cols = validate_dataset(processed_df)
            if missing_cols:
                logger_msg = f"Incomplete Dataset! Missing critical columns after mapping:\n{', '.join(missing_cols)}"
                messagebox.showwarning("Incomplete Data", logger_msg)

            # Robust State Initialization
            self.raw_df = df
            self.processed_df = processed_df
            self.working_df = self.processed_df.copy()
            
            messagebox.showinfo("Success", f"Dataset standardized and loaded!\nRows: {len(processed_df)}\nColumns: {len(processed_df.columns)}")
            
            # Populate filter dropdowns dynamically
            self.frames[DashboardPage].populate_dropdowns(self.processed_df)
            self.frames[InsightsPage].refresh_insights()

            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to load CSV file:\n{str(e)}")

    def get_data(self):
        """Returns the current working dataset safely."""
        return self.working_df

    def get_processed_data(self):
        """Returns the dataset with computed features safely."""
        return self.processed_df

    def reset_data(self):
        """Resets the working dataset to match the original processed dataset."""
        if self.processed_df is not None:
            self.working_df = self.processed_df.copy()
            return True
        return False


    # --- UI & Layout Methods ---

    def _setup_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except:
            pass

        # Frame Styles
        self.style.configure("Main.TFrame", background=self.MAIN_BG)
        self.style.configure("Content.TFrame", background="#ffffff", relief="flat")
        
        # Label Styles
        self.style.configure("Header.TLabel", 
                             background="#ffffff", 
                             font=("Segoe UI", 12, "bold"), 
                             foreground="#333333")
        
        self.style.configure("PageTitle.TLabel", 
                             background=self.MAIN_BG, 
                             foreground="#1e1e2f")

        # Filter Panel specific labels
        self.style.configure("FilterLabel.TLabel", 
                             background="#ffffff", 
                             font=("Segoe UI", 9, "bold"), 
                             foreground="#555555")

    def _init_sidebar(self):
        # App Logo/Title placeholder in Sidebar
        logo_label = tk.Label(
            self.sidebar, text="Social Lens : \nData Visualization & \nAnalytics Tool", bg=self.SIDEBAR_COLOR, 
            fg=self.ACTIVE_COLOR, font=("Segoe UI", 16, "bold"), pady=30
        )
        logo_label.pack(fill="x")

        # Sidebar Buttons Configuration
        pages = [
            ("Upload Dataset", UploadPage),
            ("Dashboard", DashboardPage),
            ("Insights", InsightsPage),
            ("Export", ExportPage)
        ]

        for text, F in pages:
            btn = tk.Label(
                self.sidebar, 
                text=f"  {text}", 
                bg=self.SIDEBAR_COLOR, 
                fg=self.TEXT_COLOR, 
                font=("Segoe UI", 11),
                anchor="w",
                cursor="hand2",
                height=2
            )
            btn.pack(fill="x", padx=0, pady=2)
            
            # Hover Events
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b))
            btn.bind("<Leave>", lambda e, b=btn: self._on_leave(b))
            btn.bind("<Button-1>", lambda e, f=F: self.show_frame(f))
            
            self.sidebar_buttons[F] = btn

    def _on_hover(self, button):
        if button["bg"] != self.ACTIVE_COLOR:
            button.configure(bg=self.HIGHLIGHT_COLOR)

    def _on_leave(self, button):
        if button["bg"] != self.ACTIVE_COLOR:
            button.configure(bg=self.SIDEBAR_COLOR)

    def show_frame(self, frame_class):
        # Raise Frame
        frame = self.frames[frame_class]
        frame.tkraise()

        # Update Header Title
        try:
            for child in frame.winfo_children():
                if isinstance(child, ttk.Label) and "PageTitle" in str(child.cget("style")):
                    self.header_label.config(text=child.cget("text"))
                    break
        except:
            pass

        # Update Sidebar Button State
        for f_class, btn in self.sidebar_buttons.items():
            if f_class == frame_class:
                btn.configure(bg=self.ACTIVE_COLOR)
            else:
                btn.configure(bg=self.SIDEBAR_COLOR)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
