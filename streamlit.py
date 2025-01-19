import streamlit as st
import pandas as pd
import plotly.express as px

# Set defaults for Plotly
px.defaults.template = 'plotly_dark'
px.defaults.color_continuous_scale = 'matter'

# Fungsi untuk memuat data dan menghasilkan visualisasi
def load_and_visualize(data_path, page_title):
    # Import data
    data = pd.read_csv(data_path)
    data['ReportDate'] = pd.to_datetime(data['ReportDate'], errors='coerce')
    data['ProductID'] = data['ProductID'].astype(str)
    data['StoreID'] = data['StoreID'].astype(str)
    data['DailySales'] = data['DailySales'].astype(int)

    # Sidebar filters
    date_min = data['ReportDate'].min()
    date_max = data['ReportDate'].max()
    start_date, end_date = st.sidebar.date_input(
        label='Rentang Waktu',
        min_value=date_min,
        max_value=date_max,
        value=[date_min, date_max]
    )
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    products = ['Semua Produk'] + sorted(list(data['ProductID'].astype(str).unique()))
    product = st.sidebar.selectbox(label='Produk', options=products)

    stores = ['Semua Toko'] + sorted(list(data['StoreID'].astype(str).unique()))
    store = st.sidebar.selectbox(label='Toko', options=stores)

    # Filter data
    outputs = data[(data['ReportDate'] >= start_date) & (data['ReportDate'] <= end_date)]
    if product != "Semua Produk":
        outputs = outputs[outputs['ProductID'] == product]
    if store != "Semua Toko":
        outputs = outputs[outputs['StoreID'] == store]

    # Display metrics
    st.header(f'Dashboard Penjualan {page_title}')
    max_date = outputs['ReportDate'].max()
    total_cumulatif = outputs[outputs['ReportDate']==max_date]['SalesCumulativeSum'].sum()
    total_orders = outputs[outputs['DailySales'] > 0].shape[0]
    total_sales_value = outputs['DailySales'].sum()
    avg_sales = outputs.groupby('ReportDate')['DailySales'].sum().reset_index()[1:]['DailySales'].mean()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Penjualan Kumulatif", f"{int(total_cumulatif):,}")
    with col2:
        st.metric("Total Pesanan", f"{total_orders:,}")
    with col3:
        st.metric("Total Penjualan", f"{total_sales_value:,}")
    with col4:
        st.metric("Rata-rata Penjualan Harian", f"{avg_sales:,.1f}")
    
    # Visualize cumulative sales
    cmltv = outputs.groupby('ReportDate')['SalesCumulativeSum'].sum().reset_index()
    fig = px.line(
        cmltv, 
        x='ReportDate', 
        y='SalesCumulativeSum', 
        title='Trend Penjualan Kumulatif'
    )
    fig.update_traces(
        line=dict(color='#800020'),  # Warna garis
        fill='tozeroy'           # Mengisi area di bawah garis
    )
    # Mengatur sumbu y agar tidak dimulai dari 0
    y_min = cmltv['SalesCumulativeSum'].min() * 0.99  # Margin 5% di bawah nilai minimum
    y_max = cmltv['SalesCumulativeSum'].max() * 1.001  # Margin 5% di atas nilai maksimum
    fig.update_yaxes(range=[y_min, y_max])
    st.plotly_chart(fig)

    # Visualize trend
    trend = outputs.groupby('ReportDate')['DailySales'].sum().reset_index()
    fig = px.line(trend, x='ReportDate', y='DailySales', title='Trend Penjualan Harian')
    fig.update_traces(line=dict(color='#800020'))
    st.plotly_chart(fig)

    # Top products
    product_sales = outputs.groupby('ProductID')['DailySales'].sum().nlargest(10).sort_values()
    fig = px.bar(product_sales, orientation='h', color=product_sales, title='10 Produk dengan Penjualan Terbesar', labels={"ProductID": "ID Produk", "value": "Total Penjualan"})
    st.plotly_chart(fig)

    # Top stores
    store_sales = outputs.groupby('StoreID')['DailySales'].sum().nlargest(10).sort_values()
    fig = px.bar(store_sales, orientation='h', color=store_sales, title='10 Toko dengan Penjualan Terbesar', labels={"StoreID": "ID Toko", "value": "Total Penjualan"})
    st.plotly_chart(fig)

# Sidebar navigation
st.sidebar.title("Navigasi")
page = st.sidebar.radio("Pilih Halaman", ["Dashboard Setelah Dibersihkan", "Dashboard Sebelum Dibersihkan"])

if page == "Dashboard Setelah Dibersihkan":
    load_and_visualize("data_bersih.csv", "Data Bersih")
elif page == "Dashboard Sebelum Dibersihkan":
    load_and_visualize("data_kotor.csv", "Data Kotor")
