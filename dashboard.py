import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Device Lifecycle Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling - Purple theme
st.markdown("""
<style>
    /* Set sidebar width */
    section[data-testid="stSidebar"] {
        width: 350px !important; /* Adjust this value to your preference */
    }
    
    /* Adjust main content area to account for sidebar width */
    .main .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #4B0082;
        margin-bottom: 2rem;
        
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        color: black;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 2px solid #9932CC;
    }
    .metric-container h2 {
        color: #9932CC;
        margin: 0;
    }
    .device-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #8A2BE2;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .device-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .category-badge {
        display: inline-block;
        background: #9932CC;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .duration-badge {
        display: inline-block;
        background: #663399;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .sidebar .sidebar-content {
        background: #E6E6FA;
    }
    .stSelectbox > div > div {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for treemap selection
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None
if 'selected_brand' not in st.session_state:
    st.session_state.selected_brand = 'All Brands'
if 'duration_range' not in st.session_state:
    st.session_state.duration_range = None

@st.cache_data
def load_data():
    """Load the device lifecycle data from Excel file"""
    try:
        # Load the data - adjust path as needed
        df = pd.read_excel('lifecycledata.xlsx')
        
        # Clean column names and data
        df = df.drop(df.columns[0], axis=1)  # Remove the unnamed first column
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['End Date'] = pd.to_datetime(df['End Date'])
        
        # Calculate additional metrics
        df['Start Year'] = df['Start Date'].dt.year
        df['End Year'] = df['End Date'].dt.year
        
        return df
    except FileNotFoundError:
        # Create sample data if file not found (for demo purposes)
        st.error("Excel file not found. Please ensure 'lifecycledata.xlsx' is in the same directory.")
        return None

def create_device_card(device_info):
    """Create a styled device information card"""
    return f"""
    <div class="device-card">
        <h3 style="margin-top: 0; color: #4B0082;">{device_info['Device Name']}</h3>
        <p><strong>Brand:</strong> {device_info['Brand']}</p>
        <div style="margin: 1rem 0;">
            <span class="category-badge">{device_info['Device Category']}</span>
            <span class="duration-badge">{device_info['Duration']:.1f} years</span>
        </div>
        <p><strong>Active Period:</strong> {device_info['Start Date'].strftime('%b %Y')} - {device_info['End Date'].strftime('%b %Y')}</p>
        <p><strong>Discontinuation Reason:</strong> {device_info['Reason for Discontinuing']}</p>
    </div>
    """

def main():
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Initialize duration range if not set
    if st.session_state.duration_range is None:
        st.session_state.duration_range = (float(df['Duration'].min()), float(df['Duration'].max()))
    
    # Main header
    st.markdown('<h1 class="main-header">Device Lifecycle Dashboard</h1>', unsafe_allow_html=True)
    
    # Project description moved to sidebar (above filters)
    st.sidebar.markdown(
        """
        <div style='margin-bottom: 2rem; padding: 1rem; background: white; border-radius: 10px; border: 2px solid #9932CC;'>
            <h4 style='margin-top: 0; color: black;'>Project Description</h4>
            <p style='margin-bottom: 1rem; color: black; line-height: 1.6;'>
                The device lifecycle data presented in this dashboard is sourced from the 
                <strong>Electronic Waste Graveyard</strong> project by the U.S. PIRG Education Fund. 
                This comprehensive database tracks over 100 consumer tech products that have been 
                rendered unusable due to lack of software support or server shutdowns since 2014.
            </p>
            <p style='margin-bottom: 0; color: black; font-size: 0.95rem;'>
                Source: U.S. PIRG Education Fund. (2025). <em>Electronic Waste Graveyard</em>. 
                Retrieved from <a href="https://pirg.org/edfund/resources/electronic-waste-graveyard/" 
                target="_blank" style="color: #9932CC;">https://pirg.org/edfund/resources/electronic-waste-graveyard/</a>
            </p> 
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <div style='text-align: center; margin-top: -1.5rem; margin-bottom: 2rem;'>
            <p style='font-size: 1.2rem; color: #666;'>A small project by Payam Saeedi</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Sidebar filters
    st.sidebar.markdown("## Filters")
    
    # Brand filter
    all_brands = ['All Brands'] + sorted(df['Brand'].unique().tolist())
    selected_brand = st.sidebar.selectbox(
        "Select Brand",
        all_brands,
        index=all_brands.index(st.session_state.selected_brand) if st.session_state.selected_brand in all_brands else 0,
        key='brand_selectbox'
    )
    st.session_state.selected_brand = selected_brand
    
    # Category filter - synchronized with treemap selection
    all_categories = ['All Categories'] + sorted(df['Device Category'].unique().tolist())
    
    if st.session_state.selected_category and st.session_state.selected_category in df['Device Category'].unique():
        default_category_index = all_categories.index(st.session_state.selected_category)
    elif st.session_state.selected_category is None:
        default_category_index = 0
    else:
        default_category_index = 0
    
    selected_category = st.sidebar.selectbox(
        "Select Device Category",
        all_categories,
        index=default_category_index,
        key='category_selectbox'
    )
    
    if selected_category != 'All Categories':
        st.session_state.selected_category = selected_category
    elif selected_category == 'All Categories' and not hasattr(st.session_state, '_from_treemap'):
        st.session_state.selected_category = None
    
    # Duration range filter
    min_duration, max_duration = float(df['Duration'].min()), float(df['Duration'].max())
    duration_range = st.sidebar.slider(
        "Device Lifecycle Duration (years)",
        min_duration, max_duration,
        st.session_state.duration_range,
        step=0.1,
        key='duration_slider'
    )
    st.session_state.duration_range = duration_range
    
    # Clear selection button
    if st.sidebar.button("Clear All Filters"):
        st.session_state.selected_category = None
        st.session_state.selected_brand = 'All Brands'
        st.session_state.duration_range = (min_duration, max_duration)
        st.rerun()
    
    # Apply filters
    filtered_df = df.copy()
    if st.session_state.selected_brand != 'All Brands':
        filtered_df = filtered_df[filtered_df['Brand'] == st.session_state.selected_brand]
    if st.session_state.selected_category is not None and st.session_state.selected_category != 'All Categories':
        filtered_df = filtered_df[filtered_df['Device Category'] == st.session_state.selected_category]
    filtered_df = filtered_df[
        (filtered_df['Duration'] >= st.session_state.duration_range[0]) & 
        (filtered_df['Duration'] <= st.session_state.duration_range[1])
    ]
    
    # Sidebar chart - Reasons for Discontinuing
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Reasons for Discontinuing")
    reason_counts = filtered_df['Reason for Discontinuing'].value_counts()
    fig_reasons = px.bar(
        x=reason_counts.values,
        y=reason_counts.index,
        orientation='h',
        color_discrete_sequence=['#9932CC']
    )
    fig_reasons.update_layout(
        xaxis_title="Count",
        yaxis_title="",
        height=max(250, len(reason_counts) * 30),
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=30),
        font=dict(size=10),
        hovermode=False
    )
    fig_reasons.update_traces(
        texttemplate='%{x}',
        textposition='outside',
        textfont_size=10,
        hovertemplate=None,
        hoverinfo='skip'
    )
    st.sidebar.plotly_chart(fig_reasons, use_container_width=True)
    st.sidebar.caption(f"Based on {len(filtered_df)} filtered devices")
    
    # Main content
    if len(filtered_df) == 0:
        st.warning("No devices match the selected filters. Please adjust your selection.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h2>{len(filtered_df)}</h2>
            <p>Total Devices</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        avg_duration = filtered_df['Duration'].mean()
        st.markdown(f"""
        <div class="metric-container">
            <h2>{avg_duration:.1f}</h2>
            <p>Avg Lifecycle (years)</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        unique_brands = filtered_df['Brand'].nunique()
        st.markdown(f"""
        <div class="metric-container">
            <h2>{unique_brands}</h2>
            <p>Unique Brands</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        unique_categories = filtered_df['Device Category'].nunique()
        st.markdown(f"""
        <div class="metric-container">
            <h2>{unique_categories}</h2>
            <p>Device Categories</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Timeline chart
    st.subheader("Device Support Timeline")
    st.markdown(
        """
        <p style='color: #666; font-size: 0.9rem; margin-top: -0.5rem; margin-bottom: 1rem;'>
        Hover over any point on the timeline to view full product information
        </p>
        """,
        unsafe_allow_html=True
    )
    
    timeline_data = []
    for idx, device in filtered_df.iterrows():
        timeline_data.append({
            'Device': device['Device Name'],
            'Category': device['Device Category'],
            'Brand': device['Brand'],
            'Start': device['Start Date'],
            'End': device['End Date'],
            'Duration': device['Duration'],
            'Reason': device['Reason for Discontinuing']
        })
    timeline_df = pd.DataFrame(timeline_data)
    
    fig_timeline = go.Figure()
    timeline_color = '#9932CC'
    for idx, row in timeline_df.iterrows():
        fig_timeline.add_trace(go.Scatter(
            x=[row['Start'], row['End']],
            y=[idx, idx],
            mode='lines+markers',
            line=dict(color=timeline_color, width=6),
            marker=dict(size=8, color=timeline_color),
            name=row['Category'],
            legendgroup=row['Category'],
            showlegend=row['Category'] not in [trace.name for trace in fig_timeline.data],
            hovertemplate=(
                f"<b>{row['Device']}</b><br>" +
                f"Brand: {row['Brand']}<br>" +
                f"Category: {row['Category']}<br>" +
                f"Support: {row['Start'].strftime('%b %Y')} - {row['End'].strftime('%b %Y')}<br>" +
                f"Duration: {row['Duration']:.1f} years<br>" +
                f"Reason: {row['Reason']}<br>" +
                "<extra></extra>"
            )
        ))
    fig_timeline.update_layout(
        height=max(400, len(timeline_df) * 25),
        xaxis_title="Date",
        yaxis_title="Devices",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(timeline_df))),
            ticktext=[f"{row['Device'][:30]}..." if len(row['Device']) > 30 else row['Device'] 
                     for _, row in timeline_df.iterrows()],
            tickfont=dict(size=10)
        ),
        showlegend=False,
        margin=dict(l=150)
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Device details
    st.markdown("---")
    st.subheader(f"Device Details ({len(filtered_df)} devices)")
    
    sort_options = {
        'Device Name': 'Device Name',
        'Duration (Shortest First)': 'Duration',
        'Duration (Longest First)': 'Duration_desc',
        'Start Date (Newest First)': 'Start Date_desc',
        'Start Date (Oldest First)': 'Start Date'
    }
    sort_by = st.selectbox("Sort by:", list(sort_options.keys()))
    
    if sort_by == 'Duration (Longest First)':
        display_df = filtered_df.sort_values('Duration', ascending=False)
    elif sort_by == 'Start Date (Newest First)':
        display_df = filtered_df.sort_values('Start Date', ascending=False)
    elif sort_by == 'Start Date (Oldest First)':
        display_df = filtered_df.sort_values('Start Date', ascending=True)
    elif sort_by == 'Duration (Shortest First)':
        display_df = filtered_df.sort_values('Duration', ascending=True)
    else:
        display_df = filtered_df.sort_values('Device Name')
    
    for idx, device in display_df.iterrows():
        st.markdown(create_device_card(device), unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #4B0082; margin-top: 2rem;'>"
        "Device Lifecycle Dashboard | Data analysis of discontinued consumer devices"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
