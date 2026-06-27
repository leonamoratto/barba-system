import pandas as pd
import numpy as np
import datetime
import os

np.random.seed(42)

BRANCHES = ["SOUTH_ZONE", "NORTH_ZONE", "DOWNTOWN", "WEST_ZONE", "BAIXADA_ZONE"]
BARBERS = {
    "SOUTH_ZONE": ["Ronaldo Fenômeno (Cascão)", "Neymar (Moicano)"],
    "NORTH_ZONE": ["René Higuita", "Carlos Valderrama"],
    "DOWNTOWN": ["Roberto Baggio (Codino)", "Taribo West"],
    "WEST_ZONE": ["Dennis Rodman", "Allen Iverson"],
    "BAIXADA_ZONE": ["Kazuma Kuwabara", "Giorno Giovanna"]
}

SERVICES = ["Haircut", "Beard Trim", "Hair + Beard Combo", "Hair Pigmentation"]
BASE_PRICES = {
    "Haircut": 50.0, 
    "Beard Trim": 35.0, 
    "Hair + Beard Combo": 75.0, 
    "Hair Pigmentation": 90.0
}

BRANCH_MULTIPLIERS = {
    "SOUTH_ZONE": 1.6,    # 60% mais caro
    "WEST_ZONE": 1.4,     # 40% mais caro
    "DOWNTOWN": 1.0,      # Preço Base
    "NORTH_ZONE": 0.85,   # 15% de desconto
    "BAIXADA_ZONE": 0.75  # 25% de desconto
}

PAYMENT_METHODS = ["Credit Card", "Pix", "Cash", "Debit Card"]

# --- GERAÇÃO DE DADOS ---
def generate_mock_data(num_records=5000):
    """Gera um dataset sintético de vendas da barbearia."""
    print("Gerando dados sintéticos...")
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365)
    
    dates = [
        start_date + datetime.timedelta(
            seconds=np.random.randint(0, int((end_date - start_date).total_seconds()))
        ) 
        for _ in range(num_records)
    ]
    
    branches = np.random.choice(BRANCHES, num_records, p=[0.25, 0.20, 0.25, 0.15, 0.15])
    services = np.random.choice(SERVICES, num_records, p=[0.4, 0.2, 0.3, 0.1]) 
    barbers = [np.random.choice(BARBERS[branch]) for branch in branches]
    
    prices = [
        round(BASE_PRICES[service] * BRANCH_MULTIPLIERS[branch], 2) 
        for service, branch in zip(services, branches)
    ]
    
    # Adiciona gorjetas aleatórias em 30% dos casos
    tips = [np.random.randint(5, 20) if np.random.random() > 0.7 else 0 for _ in range(num_records)]
    
    # Escolhe formas de pagamento
    payments = np.random.choice(PAYMENT_METHODS, num_records, p=[0.3, 0.5, 0.05, 0.15])
    
    # Cria o DataFrame
    df = pd.DataFrame({
        "Transaction_Date": dates,
        "Branch": branches,
        "Barber_Name": barbers,
        "Service": services,
        "Base_Price": prices,
        "Tip": tips,
        "Total_Paid": np.array(prices) + np.array(tips),
        "Payment_Method": payments
    })
    
    # Ordena cronologicamente
    df = df.sort_values(by="Transaction_Date").reset_index(drop=True)
    return df

# --- SALVAMENTO ---
if __name__ == "__main__":
    df_sales = generate_mock_data(30000)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dados_dir = os.path.join(BASE_DIR, "dados")
    os.makedirs(dados_dir, exist_ok=True)
    file_path = os.path.join(dados_dir, "sales_data.parquet")
    df_sales.to_parquet(file_path, index=False)
    print(f"✅ Sucesso! Dataset com {len(df_sales)} linhas salvo em: {file_path}")
    print(df_sales.head())