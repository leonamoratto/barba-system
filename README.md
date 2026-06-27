# 💈 Barba System - Barbershop Management Hub

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

**Live Demo:** [barba-system.streamlit.app](https://barba-system.streamlit.app/)

## 📌 Project Overview
The **Barba System** is an interactive Executive Dashboard and Financial Intelligence tool designed for barbershop chains. Built entirely in Python with Streamlit, this project moves beyond simple data visualization by incorporating real-world business rules, Role-Based Access Control (RBAC), and geospatial analysis.

The goal of this portfolio piece is to demonstrate how raw operational data can be transformed into actionable insights regarding profitability, cost structures, and team performance.

## 🚀 Key Features

* **🔐 Mock JWT Authentication & RBAC:** A custom login system that simulates enterprise security. "Chairman Mode" grants access to the entire chain, while "Baller Mode" restricts managers to their specific branch.
* **💼 Deep Dive Financials:** Calculates true net profit by dynamically processing variable costs (payment fees, taxes, senior/junior barber commissions) and fixed operational costs (rent) based on the filtered period.
* **🗺️ Geospatial Turf Analysis:** Uses `Folium` and `OpenStreetMap` to cluster client distribution over the last 14 days, identifying high-value (VIP) clients and regional penetration.
* **⚙️ Synthetic Data Generator:** Includes a robust data generation script (`gerador.py`) that simulates realistic business patterns, including regional pricing multipliers and varied service demands.

## 🛠️ Tech Stack
* **Frontend/Framework:** Streamlit (with custom CSS for Tableau-style KPIs)
* **Data Manipulation:** Pandas, NumPy
* **Data Visualization:** Plotly Express, Folium, Streamlit-Folium
* **Security:** PyJWT

## 💻 How to Run Locally

1. Clone this repository:
   ```bash
   git clone [https://github.com/leonamoratto/barba-system.git](https://github.com/leonamoratto/barba-system.git)

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

3. Run the application:
  ```bash

   streamlit run app.py
