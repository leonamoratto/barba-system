import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. "TABLEAU PREMIUM" STYLE CSS ---
def inject_kpi_css():
    st.markdown("""
    <style>
        hr {
            margin: 0.5em 0 !important;
            border-top: 1px solid rgba(128,128,128,0.2) !important;
        }
        
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
        .kpi-revenue { border-bottom-color: #2ECC71; } /* Green */
        .kpi-varcost { border-bottom-color: #E67E22; } /* Orange */
        .kpi-fixedcost { border-bottom-color: #E74C3C; } /* Red */
        .kpi-netprofit { border-bottom-color: #9B59B6; } /* Purple */
        
        .kpi-title {
            font-size: 0.9rem;
            color: gray;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 1.8rem;
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
    def load_process_financial_data():
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(CURRENT_DIR)
        path = os.path.join(BASE_DIR, "dados", "sales_data.parquet")
        df = pd.read_parquet(path)
        
        df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
        df['Year_Month'] = df['Transaction_Date'].dt.strftime('%Y-%m')
        df['Tax_ISS'] = df['Total_Paid'] * 0.05
        df['Payment_Fee'] = df.apply(
            lambda row: row['Total_Paid'] * 0.025 if row['Payment_Method'] == 'Credit Card' 
            else (row['Total_Paid'] * 0.01 if row['Payment_Method'] == 'Debit Card' else 0), axis=1
        )
        # 3. Comissão por Senioridade do Barbeiro
        commission_rates = {"Ronaldo Fenômeno (Cascão)": 0.40, "Neymar (Moicano)": 0.25, 
                            "René Higuita": 0.40, "Carlos Valderrama": 0.25, 
                            "Roberto Baggio (Codino)": 0.40, "Taribo West": 0.25,
                            "Dennis Rodman": 0.40, "Allen Iverson": 0.25, 
                            "Kazuma Kuwabara": 0.40, "Giorno Giovanna": 0.25}
        
        df['Commission_Rate'] = df['Barber_Name'].map(commission_rates)
        df['Barber_Commission'] = df['Base_Price'] * df['Commission_Rate']
        df['Total_Variable_Costs'] = df['Tax_ISS'] + df['Payment_Fee'] + df['Barber_Commission']
        df['Contribution_Margin'] = df['Total_Paid'] - df['Total_Variable_Costs']
        branch_fixed_costs = {"SOUTH_ZONE": 3500.00,
                            "NORTH_ZONE": 2200.00,
                            "DOWNTOWN": 2800.00,
                            "WEST_ZONE": 3200.00,
                            "BAIXADA_ZONE": 1800.00 }
        df['Monthly_Fixed_Cost_Config'] = df['Branch'].map(branch_fixed_costs).fillna(2000.00)
        
        return df

    df_full = load_process_financial_data()
    user = st.session_state["logged_user"]

    # --- RBAC ---
    if user["role"] == "RESTRICTED":
        df = df_full[df_full["Branch"] == user["branch"]]
    else:
        df = df_full

    # --- HEADER ---
    st.title("💼 Deep Dive: Money Talks")
    display_profile_badge(user)
    
    # --- DYNAMIC FILTERS ---
    st.markdown("##### 🎛️ Financial Filters")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        unique_months = sorted(df["Year_Month"].unique().tolist())
        selected_months = st.multiselect("Period (Year-Month):", unique_months)
        final_months = selected_months if selected_months else unique_months

    with col_f2:
        unique_services = df["Service"].unique().tolist()
        selected_services = st.multiselect("Services:", unique_services)
        final_services = selected_services if selected_services else unique_services

    with col_f3:
        unique_payments = df["Payment_Method"].unique().tolist()
        selected_payments = st.multiselect("Payment Method:", unique_payments)
        final_payments = selected_payments if selected_payments else unique_payments

    filtered_df = df[
        (df["Year_Month"].isin(final_months)) &
        (df["Service"].isin(final_services)) & 
        (df["Payment_Method"].isin(final_payments))
    ]

    st.markdown("<hr>", unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("⚠️ Whoa there! You filtered so hard there's no money left. Adjust your filters.")
        return

    # --- ADVANCED FINANCIAL KPIs ---
    # Custo fixo = Custo da filial * Quantidade de meses filtrados
    num_months_selected = len(final_months)
    active_branches = filtered_df["Branch"].unique()
    
    gross_revenue = filtered_df["Total_Paid"].sum()
    total_var_costs = filtered_df["Total_Variable_Costs"].sum()
    
    total_fixed_costs = 0
    for branch in active_branches:
        # Pega o custo fixo base da filial e multiplica pelos meses filtrados
        branch_cost = df[df['Branch'] == branch]['Monthly_Fixed_Cost_Config'].iloc[0]
        total_fixed_costs += (branch_cost * num_months_selected)
        
    net_profit = gross_revenue - total_var_costs - total_fixed_costs

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card kpi-revenue">
            <div class="kpi-title">Gross Revenue</div>
            <div class="kpi-value">$ {gross_revenue:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="kpi-card kpi-varcost">
            <div class="kpi-title">Taxes & Fees (Var)</div>
            <div class="kpi-value">$ {total_var_costs:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="kpi-card kpi-fixedcost">
            <div class="kpi-title">Fixed Costs (Rent)</div>
            <div class="kpi-value">$ {total_fixed_costs:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="kpi-card kpi-netprofit">
            <div class="kpi-title">Net Profit</div>
            <div class="kpi-value">$ {net_profit:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("") 
    st.write("")

    # --- CHARTS ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Profitability by Branch")
        branch_perf = filtered_df.groupby("Branch").agg(
            Revenue=('Total_Paid', 'sum'),
            Var_Costs=('Total_Variable_Costs', 'sum'),
            Fixed_Cost_Base=('Monthly_Fixed_Cost_Config', 'first')
        ).reset_index()
        
        branch_perf['Total_Fixed'] = branch_perf['Fixed_Cost_Base'] * num_months_selected
        branch_perf['Net_Profit'] = branch_perf['Revenue'] - branch_perf['Var_Costs'] - branch_perf['Total_Fixed']
        
        # Melt dataframe para plotar barras agrupadas (Receita vs Lucro)
        df_melted = pd.melt(branch_perf, id_vars=['Branch'], value_vars=['Revenue', 'Net_Profit'], 
                            var_name='Metric', value_name='Amount')
        
        fig_profit = px.bar(
            df_melted, x='Branch', y='Amount', color='Metric', barmode='group',
            color_discrete_map={'Revenue': '#2ECC71', 'Net_Profit': '#9B59B6'}
        )
        fig_profit.update_layout(
            margin=dict(t=10, b=20, l=10, r=10), height=350, paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text=''
        )
        fig_profit.update_yaxes(title="")
        fig_profit.update_xaxes(title="")
        st.plotly_chart(fig_profit, use_container_width=True)

    with col_chart2:
        st.subheader("💸 Where is the money going?")
        cost_labels = ['Net Profit', 'Variable Costs', 'Fixed Costs']
        # Usamos max(0, net_profit) para não quebrar o gráfico de pizza caso haja prejuízo no filtro
        cost_values = [max(0, net_profit), total_var_costs, total_fixed_costs]
        
        fig_donut = px.pie(
            names=cost_labels, values=cost_values, hole=0.5,
            color_discrete_sequence=['#9B59B6', '#E67E22', '#E74C3C']
        )
        fig_donut.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=350, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- SERVICE CONTRIBUTION MARGIN TABLE ---
    st.subheader("🎯 Service Contribution Margin")
    st.markdown("Which services actually leave money in the register after taxes and fees?")
    
    service_perf = filtered_df.groupby('Service').agg(
        Volume=('Total_Paid', 'count'),
        Gross_Revenue=('Total_Paid', 'sum'),
        Total_Contribution_Margin=('Contribution_Margin', 'sum')
    ).reset_index()

    service_perf['Margin_%'] = (service_perf['Total_Contribution_Margin'] / service_perf['Gross_Revenue']) * 100
    service_perf = service_perf.sort_values(by='Margin_%', ascending=False)

    st.dataframe(
        service_perf.style.format({
            'Gross_Revenue': '${:,.2f}',
            'Total_Contribution_Margin': '${:,.2f}',
            'Margin_%': '{:.1f}%'
        }).background_gradient(subset=['Margin_%'], cmap='Greens'),
        use_container_width=True,
        hide_index=True
    )