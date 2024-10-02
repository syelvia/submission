import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


sns.set(style='dark')

# Fungsi untuk menghitung jumlah pesanan per kota
def create_city_order_counts(df):
    city_order_counts = df.groupby('customer_city')['order_id'].nunique().reset_index()
    city_order_counts.columns = ['City', 'Total Orders']
    return city_order_counts

# Fungsi untuk menentukan 5 produk teratas dan terbawah di kota tertentu
def create_top_bottom_products(df, top_city_name):
    top_city_data = df[df['customer_city'] == top_city_name]
    product_order_counts = top_city_data.groupby('product_category_name')['order_id'].nunique().reset_index()
    product_order_counts.columns = ['Product Category', 'Total Orders']
    product_order_counts = product_order_counts.sort_values(by='Total Orders', ascending=False)
    top_5_products = product_order_counts.head(5)
    bottom_5_products = product_order_counts.tail(5)
    return top_5_products, bottom_5_products

# Fungsi untuk membuat DataFrame RFM
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"]).dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

# Membaca file csv
all_df = pd.read_csv("all_data.csv")
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Menghitung pesanan per kota
city_order_counts = create_city_order_counts(all_df)
top_city = city_order_counts.sort_values(by='Total Orders', ascending=False).iloc[0]
top_city_name = top_city['City']

# Mendapatkan 5 produk teratas dan terbawah di kota dengan pesanan terbanyak
top_5_products, bottom_5_products = create_top_bottom_products(all_df, top_city_name)

# Warna untuk grafik
colors = ["#72BCD4"] + ["#D3D3D3"] * 4
rfm_color = "#72BCD4" 

# Menampilkan header
st.title("Dashboard Analysis of E-commerce Data")

# Visualisasi Top 5 Kota dengan Pesanan Terbanyak
st.subheader("Top 5 Cities by Total Orders")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    y="Total Orders",
    x="City",
    data=city_order_counts.sort_values(by="Total Orders", ascending=False).head(5),
    palette=colors  
)
plt.title("Top 5 Cities by Total Orders", fontsize=15)
plt.xlabel("City", fontsize=12)
plt.ylabel("Total Orders", fontsize=12)
plt.xticks(rotation=45)
st.pyplot(fig)

# Visualisasi Produk Teratas dan Terbawah di Kota dengan Pesanan Terbanyak
st.subheader(f"Product Analysis in {top_city_name}")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(40, 20))

sns.barplot(x="Total Orders", y="Product Category", data=top_5_products, palette=colors, ax=ax[0])
ax[0].set_title("Top 5 Products by Total Orders", fontsize=40)
ax[0].set_xlabel("Total Orders", fontsize=40)
ax[0].set_ylabel("Product Category", fontsize=40)
ax[0].tick_params(axis='y', labelsize=40)
ax[0].tick_params(axis='x', labelsize=40)

sns.barplot(x="Total Orders", y="Product Category", data=bottom_5_products.sort_values(by="Total Orders", ascending=True), palette=colors, ax=ax[1])
ax[1].set_title("Bottom 5 Products by Total Orders", fontsize=40)
ax[1].set_xlabel("Total Orders", fontsize=40)
ax[1].set_ylabel("Product Category", fontsize=40)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=40)
ax[1].tick_params(axis='x', labelsize=40)

plt.suptitle(f"Product Analysis in {top_city_name}", fontsize=30)
st.pyplot(fig)

# Memfilter data berdasarkan tanggal dan membuat DataFrame RFM
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Select Date Range', min_value=min_date, max_value=max_date, value=[min_date, max_date]
    )

filtered_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                     (all_df["order_purchase_timestamp"] <= str(end_date))]

rfm_df = create_rfm_df(filtered_df)

# Menampilkan analisis RFM
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = round(rfm_df.monetary.mean(), 2) 
    st.metric("Average Monetary", value=f"${avg_monetary}")

# Visualisasi Analisis RFM menggunakan satu warna
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), color=rfm_color, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Customer ID", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha='right')  

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), color=rfm_color, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Customer ID", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha='right')  

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), color=rfm_color, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Customer ID", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, ha='right')  

st.pyplot(fig)
