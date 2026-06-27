import streamlit as st
import pandas as pd
import os
import numpy as np
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

barber_colors = {
        "Ronaldo Fenômeno (Cascão)": "#FF5733", 
        "Neymar (Moicano)": "#33FF57",          
        "René Higuita": "#3357FF",             
        "Carlos Valderrama": "#FF33A1",         
        "Roberto Baggio (Codino)": "#FFC300",  
        "Taribo West": "#8E44AD",              
        "Dennis Rodman": "#E74C3C",             
        "Allen Iverson": "#16A085",             
        "Kazuma Kuwabara": "#2C3E50",          
        "Giorno Giovanna": "#F39C12"           
    }

def renderizar():
    st.title("🗺️ Strategic Coverage & Turf - Last 2 weeks")
    st.markdown("Interactive client distribution. Zoom in to expand clusters and find VIP clients who contributed the most in the tip jar!!")
    
    user = st.session_state["logged_user"]

    if user["role"] == "TOTAL":
        st.warning("🚨 Attention! 🚨 For admin acess, data may take a while to load. Use the filters to reduce the data size.")
    if user["role"] == "RESTRICTED":
        st.info(f"📌 Baller Mode: You are viewing only the clients from {user['branch'].replace('_', ' ')}.")
    
    @st.cache_data
    def load_data():
        path = os.path.join("dados", "sales_data.parquet")
        return pd.read_parquet(path)

    df_full = load_data()
    df_full['Transaction_Date'] = pd.to_datetime(df_full['Transaction_Date'])
    cutoff_date = df_full['Transaction_Date'].max() - pd.Timedelta(days=14)
    df_full = df_full[df_full['Transaction_Date'] >= cutoff_date]

    if user["role"] == "RESTRICTED":
        df_full = df_full[df_full["Branch"] == user["branch"]]

    # --- DYNAMIC MAP FILTERS (Empty = All) ---
    st.markdown("##### 🎛️ Map Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if user["role"] == "TOTAL":
            branches = df_full["Branch"].unique().tolist()
            selected_branches = st.multiselect("Branch Turf:", branches)
            final_branches = selected_branches if selected_branches else branches
        else:
            final_branches = [user["branch"]]
            st.multiselect("Branch Turf:", final_branches, default=final_branches, disabled=True)
            
    with col2:
        barbers = df_full[df_full["Branch"].isin(final_branches)]["Barber_Name"].unique().tolist()
        selected_barbers = st.multiselect("Barbers:", barbers)
        final_barbers = selected_barbers if selected_barbers else barbers
        
    with col3:
        services = df_full["Service"].unique().tolist()
        selected_services = st.multiselect("Services:", services)
        final_services = selected_services if selected_services else services

    # Apply Filters
    df_filtered = df_full[
        (df_full["Branch"].isin(final_branches)) &
        (df_full["Barber_Name"].isin(final_barbers)) &
        (df_full["Service"].isin(final_services)) &
        (df_full["Tip"] > 0)
    ].copy() 

    if df_filtered.empty:
        st.warning("⚠️ No clients found with these filters. They must be getting haircuts somewhere else!")
        return

    # --- GEOSPATIAL LOGIC ---
    coords_mapping = {
        "DOWNTOWN": {"lat": -22.9068, "lon": -43.1729},
        "SOUTH_ZONE": {"lat": -22.9711, "lon": -43.1822},
        "NORTH_ZONE": {"lat": -22.8869, "lon": -43.2776},
        "WEST_ZONE": {"lat": -23.0036, "lon": -43.3117},
        "BAIXADA_ZONE": {"lat": -22.7561, "lon": -43.4607}
    }

    np.random.seed(42) 
    
    def generate_safe_coords(row):
        base_lat = coords_mapping.get(row["Branch"], {}).get("lat", -22.9)
        base_lon = coords_mapping.get(row["Branch"], {}).get("lon", -43.2)
        
        if row["Branch"] == "SOUTH_ZONE":
            lat = base_lat + np.random.uniform(0, 0.025)
            lon = base_lon + np.random.uniform(-0.025, 0)
        elif row["Branch"] == "DOWNTOWN":
            lat = base_lat + np.random.uniform(-0.010, 0.005)
            lon = base_lon + np.random.uniform(-0.035, -0.005)
        elif row["Branch"] == "WEST_ZONE":
            lat = base_lat + np.random.uniform(0, 0.03)
            lon = base_lon + np.random.uniform(-0.03, 0.03)
        else:
            lat = base_lat + np.random.normal(0, 0.02)
            lon = base_lon + np.random.normal(0, 0.02)
            
        return pd.Series({"lat": lat, "lon": lon})

    df_filtered[["lat", "lon"]] = df_filtered.apply(generate_safe_coords, axis=1)
    start_lat = df_filtered["lat"].mean()
    start_lon = df_filtered["lon"].mean()
    zoom_start = 10 if user["role"] == "TOTAL" else 13

    # Changed tiles to OpenStreetMap for a realistic GPS look
    m = folium.Map(location=[start_lat, start_lon], zoom_start=zoom_start, tiles="OpenStreetMap")

    marker_cluster = MarkerCluster().add_to(m)

    sample_size = min(1000, len(df_filtered))
    df_sample = df_filtered.sample(sample_size)

    col_map, col_info = st.columns([0.7, 0.3])
    
    with col_map:
        m = folium.Map(location=[start_lat, start_lon], zoom_start=zoom_start, tiles="OpenStreetMap")
        marker_cluster = MarkerCluster().add_to(m)
        
        for idx, row in df_sample.iterrows():
            pin_color = barber_colors.get(row["Barber_Name"], "#95a5a6")
            is_vip = row["Total_Paid"] > 70
            popup_html = f"""
                            <div style="font-family: Arial, sans-serif; min-width: 150px;">
                                <h4 style="margin-top:0; color: {pin_color};">{'👑 VIP Client' if is_vip else '✂️ Barber: ' + row['Barber_Name']}</h4>
                                <b>Service:</b> {row['Service']}<br>
                                <b>Tip:</b> ${row['Tip']:.2f}<br>
                                <b>Barber:</b> {row['Barber_Name']}
                            </div>
                            """
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=8 if is_vip else 5,
                popup=folium.Popup(popup_html, max_width=250),
                color=pin_color,
                fill=True,
                fill_color=pin_color,
                fill_opacity=0.9
            ).add_to(marker_cluster)
        
        st_folium(m, use_container_width=True, height=500)

    with col_info:
        with st.container(border=True):
            st.markdown("### 📍 Map Legend")
            st.metric(label="Total Clients on Map", value=len(df_filtered))
            html_rows = ""
            barber_counts = df_filtered.groupby("Barber_Name").size().sort_values(ascending=False)
            
            for barber, count in barber_counts.items():
                color = barber_colors.get(barber, "#95a5a6")
                if barber in barber_counts.index:
                    html_rows += f"""
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 5px;">
                    <div style="display: flex; align-items: center;">
                        <span style="display: inline-block; width: 12px; height: 12px; background-color: {color}; border-radius: 50%; margin-right: 8px;"></span>
                        <span style="font-size: 0.85em;">{barber}</span>
                    </div>
                    <div style="font-weight: bold; font-size: 0.9em;">{count}</div>
                </div>
                """
            
            st.html(f"""
            <div style="font-family: sans-serif; line-height: 1.5;">
                {html_rows}
            </div>
            """)