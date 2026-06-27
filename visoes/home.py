import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. "TABLEAU PREMIUM" STYLE CSS ---
def inject_kpi_css():
    st.markdown("""
    <style>
        /* Goodbye giant st.divider */
        hr {
            margin: 0.5em 0 !important;
            border-top: 1px solid rgba(128,128,128,0.2) !important;
        }
        
        /* KPI Cards with Hover Effect and Colored Borders */
        .kpi-card {
            background-color: rgba(128, 128, 128, 0.05);
            border-radius: 12px;
            padding: 20px 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
            border-bottom: 4px solid transparent;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
        }
        .kpi-revenue { border-bottom-color: #2ECC71; }
        .kpi-ticket { border-bottom-color: #3498DB; }
        .kpi-tips { border-bottom-color: #F1C40F; }
        
        .kpi-title {
            font-size: 0.9rem;
            color: gray;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 800;
            margin: 0;
        }
    </style>
    """, unsafe_allow_html=True)

def display_profile_badge(user):
    if user["role"] == "TOTAL":
        html = f"<div style='margin-bottom: 15px;'><span style='background-color: rgba(255, 165, 0, 0.2); color: #cc7000; padding: 4px 12px; border-radius: 15px; font-weight: bold;'>👑 Chairman Mode | Viewing: {user['branch'].replace('_', ' ')}</span></div>"
    else:
        html = f"<div style='margin-bottom: 15px;'><span style='background-color: rgba(46, 134, 193, 0.2); color: #2E86C1; padding: 4px 12px; border-radius: 15px; font-weight: bold;'>✂️ Baller Mode | Viewing: {user['branch'].replace('_', ' ')}</span></div>"
    st.markdown(html, unsafe_allow_html=True)


# --- 2. INTERACTIVE DASHBOARD ENGINE ---
def renderizar():
    inject_kpi_css()
    
    @st.cache_data
    def load_data():
        path = os.path.join("dados", "sales_data.parquet")
        return pd.read_parquet(path)

    df_full = load_data()
    user = st.session_state["logged_user"]

    # RBAC remains strong
    if user["role"] == "RESTRICTED":
        df = df_full[df_full["Branch"] == user["branch"]]
    else:
        df = df_full

    # --- HEADER ---
    st.title("⚽ Banter & Bottom Line")
    display_profile_badge(user)
    
    # --- DYNAMIC FILTERS (The Magic) ---
    st.markdown("##### 🎛️ Matchday Filters")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        unique_services = df["Service"].unique().tolist()
        selected_services = st.multiselect("Services:", unique_services)
        final_services = selected_services if selected_services else unique_services

    with col_f2:
        unique_payments = df["Payment_Method"].unique().tolist()
        selected_payments = st.multiselect("Payment Method:", unique_payments)
        final_payments = selected_payments if selected_payments else unique_payments

    filtered_df = df[
        (df["Service"].isin(final_services)) & 
        (df["Payment_Method"].isin(final_payments))
    ]

    st.markdown("<hr>", unsafe_allow_html=True)

    # Prevent breaking the app if all filters are cleared
    if filtered_df.empty:
        st.warning("⚠️ Whoa there! You filtered so hard there are no haircuts left. Pick at least one service.")
        return

    # --- TURBOCHARGED KPIs ---
    col1, col2, col3 = st.columns(3)
    
    revenue = filtered_df["Total_Paid"].sum()
    ticket = filtered_df["Total_Paid"].mean()
    tips = filtered_df["Tip"].sum()
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card kpi-revenue">
            <div class="kpi-title">💸 Total Revenue</div>
            <div class="kpi-value">$ {revenue:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="kpi-card kpi-ticket">
            <div class="kpi-title">💳 Average Ticket</div>
            <div class="kpi-value">$ {ticket:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="kpi-card kpi-tips">
            <div class="kpi-title">🍻 Tip Jar</div>
            <div class="kpi-value">$ {tips:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("") 
    st.write("")

    # --- SIDE-BY-SIDE CHARTS ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        payment_df = filtered_df.groupby("Payment_Method")["Total_Paid"].sum().reset_index()
        fig_pay = px.pie(
            payment_df, values='Total_Paid', names='Payment_Method',
            title='How is the crowd paying? 💰', hole=0.45,
            color_discrete_sequence=px.colors.sequential.Plotly3
        )
        # Remove background and adjust margins
        fig_pay.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=320, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pay, use_container_width=True)

    with col_chart2:
        service_counts = filtered_df["Service"].value_counts().reset_index()
        service_counts.columns = ["Service", "Count"]
        fig_serv = px.bar(
            service_counts, x="Count", y="Service", orientation='h',
            title="Hottest items on the chair? 💈",
            color="Count", color_continuous_scale="Teal"
        )
        fig_serv.update_layout(showlegend=False, margin=dict(t=40, b=10, l=10, r=10), height=320, paper_bgcolor="rgba(0,0,0,0)")
        fig_serv.update_yaxes(categoryorder="total ascending", title="")
        st.plotly_chart(fig_serv, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- BARBER RANKING (WITH MEDALS) ---
    st.subheader("🏆 Top Scoring Barbers (Revenue)")
    
    # Group and sort to award medals
    barber_perf = filtered_df.groupby("Barber_Name")["Total_Paid"].sum().sort_values(ascending=False).reset_index()
    
    # Dynamic emoji medals for the Top 3
    medals = ['🥇 ', '🥈 ', '🥉 ']
    barber_perf['Barber_Name_Display'] = [
        medals[i] + name if i < 3 else '🧔🏽‍♂️ ' + name 
        for i, name in enumerate(barber_perf['Barber_Name'])
    ]
    
    fig_barber = px.bar(
        barber_perf, 
        x="Total_Paid", 
        y="Barber_Name_Display",
        text_auto='.2s',
        color="Total_Paid",
        color_continuous_scale="Turbo" 
    )
    
    fig_barber.update_layout(
        showlegend=False, 
        margin=dict(t=10, b=20, l=10, r=10), 
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis={'categoryorder':'total ascending'} 
    )
    fig_barber.update_yaxes(title="")
    fig_barber.update_xaxes(title="Revenue ($)")
    
    st.plotly_chart(fig_barber, use_container_width=True)