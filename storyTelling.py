# ========================================
# STORYTELLING: HOSPITAL BEDS MANAGEMENT
# ========================================


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import squarify
from datetime import datetime
import os # Import os module untuk manipulasi folder

# 1. LOAD DATA
df_pat = pd.read_csv('patients.csv')
df_srv = pd.read_csv('services_weekly.csv')

print("=== INFO DATA ===")
print("patients.csv:", df_pat.shape)
print("services_weekly.csv:", df_srv.shape)

# 2. STANDARISASI DAN PEMBERSIHAN DASAR
df_pat.columns = [c.strip().lower().replace(" ", "_") for c in df_pat.columns]
df_srv.columns = [c.strip().lower().replace(" ", "_") for c in df_srv.columns]

# Cek kolom arrival & departure di patients.csv
arrival_col = None
departure_col = None
for col in df_pat.columns:
    if 'arrival' in col.lower():
        arrival_col = col
    if 'departure' in col.lower():
        departure_col = col

print("\nKolom Arrival:", arrival_col)
print("Kolom Departure:", departure_col)

# Pastikan kolom ditemukan
if not arrival_col or not departure_col:
    raise ValueError("Kolom Arrival dan Departure tidak ditemukan di patients.csv")

# 3. KONVERSI FORMAT TANGGAL DAN HITUNG DURASI RAWAT
df_pat[arrival_col] = pd.to_datetime(df_pat[arrival_col], errors='coerce')
df_pat[departure_col] = pd.to_datetime(df_pat[departure_col], errors='coerce')

df_pat = df_pat.dropna(subset=[arrival_col, departure_col])
df_pat['stay_duration_days'] = (df_pat[departure_col] - df_pat[arrival_col]).dt.days
df_pat = df_pat[df_pat['stay_duration_days'] >= 0]

# 4. TAMBAHKAN ATRIBUT WAKTU
df_pat['month'] = df_pat[arrival_col].dt.to_period('M').astype(str)
df_pat['week'] = df_pat[arrival_col].dt.isocalendar().week
df_pat['year'] = df_pat[arrival_col].dt.year

print("\n=== DATASET PATIENTS BERSIH ===")
print(df_pat.info())

# ========================================
# 5. ANALISIS DAN VISUALISASI
# ========================================

# Buat folder untuk menyimpan visualisasi
output_folder = 'visualizations'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"\nFolder '{output_folder}' dibuat.")


# --- 1. LINE CHART: Tren rata-rata lama rawat per minggu ---
trend = df_pat.groupby(['year','week'])['stay_duration_days'].mean().reset_index()
trend['periode'] = trend['year'].astype(str) + '-W' + trend['week'].astype(str)

fig1 = px.line(trend, x='periode', y='stay_duration_days',
               title='Rata-rata Lama Rawat Pasien per Minggu',
               labels={'stay_duration_days': 'Durasi Rawat (Hari)', 'periode': 'Periode Minggu'})
# Simpan sebagai gambar
fig1.write_image(os.path.join(output_folder, 'line_chart_lama_rawat_mingguan.png'))
print("Line Chart disimpan di:", os.path.join(output_folder, 'line_chart_lama_rawat_mingguan.png'))
# Jika Anda tetap ingin menampilkan juga, biarkan fig1.show()
# fig1.show()
# 
# 
# 
# 
# 


# --- 2. HEATMAP: Durasi rata-rata per layanan dan bulan ---
if 'service' in df_pat.columns:
    heatmap_data = df_pat.groupby(['service','month'])['stay_duration_days'].mean().unstack(fill_value=0)
    plt.figure(figsize=(12,6))
    sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt=".1f")
    plt.title('Heatmap Durasi Rawat per Layanan dan Bulan')
    plt.xlabel('Bulan')
    plt.ylabel('Layanan')
    plt.tight_layout()
    # Simpan sebagai gambar
    plt.savefig(os.path.join(output_folder, 'heatmap_durasi_rawat_layanan_bulan.png'))
    print("Heatmap disimpan di:", os.path.join(output_folder, 'heatmap_durasi_rawat_layanan_bulan.png'))
    plt.close() # Tutup plot agar tidak mengganggu plot selanjutnya
    # 
    # 
    # 
    # 
else:
    print("Kolom 'service' tidak ditemukan. Heatmap dilewati.")

# --- 3. TREEMAP: Proporsi jumlah pasien per layanan ---
if 'service' in df_pat.columns:
    tree_data = df_pat['service'].value_counts().reset_index()
    tree_data.columns = ['service', 'jumlah_pasien']
    plt.figure(figsize=(12,6))
    squarify.plot(sizes=tree_data['jumlah_pasien'],
                  label=[f"{a}\n{b}" for a,b in zip(tree_data['service'], tree_data['jumlah_pasien'])],
                  alpha=0.8)
    plt.title('Treemap Jumlah Pasien per Layanan')
    plt.axis('off')
    # Simpan sebagai gambar
    plt.savefig(os.path.join(output_folder, 'treemap_jumlah_pasien_layanan.png'))
    print("Treemap disimpan di:", os.path.join(output_folder, 'treemap_jumlah_pasien_layanan.png'))
    plt.close() # Tutup plot
    # 
    # 
    # 
    # 
else:
    print("Kolom 'service' tidak ditemukan. Treemap dilewati.")

# --- 4. SCATTER PLOT: Korelasi usia dan lama rawat ---
if 'age' in df_pat.columns:
    fig4 = px.scatter(df_pat, x='age', y='stay_duration_days',
                      color='service' if 'service' in df_pat.columns else None,
                      trendline='ols',
                      title='Korelasi Usia Pasien vs Lama Rawat',
                      labels={'age':'Usia Pasien', 'stay_duration_days':'Durasi Rawat (Hari)'})
    # Simpan sebagai gambar
    fig4.write_image(os.path.join(output_folder, 'scatter_plot_usia_lama_rawat.png'))
    print("Scatter Plot disimpan di:", os.path.join(output_folder, 'scatter_plot_usia_lama_rawat.png'))
    # fig4.show()
    # 
    # 
    # 
    # 
else:
    print("Kolom 'age' tidak ditemukan untuk scatter.")

# ========================================
# 6. STORYTELLING OUTPUT (DASHBOARD FLOW)
# ========================================
print("""
=== STORYTELLING FLOW ===

1. Line Chart:
    - Menunjukkan perubahan rata-rata lama rawat dari minggu ke minggu.
    - Periode dengan kenaikan bisa menandakan peningkatan kompleksitas kasus.

2. Heatmap:
    - Menunjukkan layanan mana yang memiliki durasi rawat tinggi tiap bulan.
    - Warna gelap = beban tinggi.

3. Treemap:
    - Menampilkan distribusi pasien per layanan.
    - Kotak terbesar = layanan dengan volume pasien terbanyak.

4. Scatter Plot:
    - Menganalisis hubungan usia pasien terhadap lama rawat.
    - Jika tren naik, usia lanjut cenderung dirawat lebih lama.

Insight yang bisa diambil:
- Layanan dengan durasi rawat tinggi perlu evaluasi efisiensi.
- Minggu dengan durasi puncak bisa dianalisis penyebabnya (musiman, outbreak, dll).
- Scatter menunjukkan pola kompleksitas pasien.
""")

# ========================================
# 7. SIMPAN HASIL
# ========================================
df_pat.to_csv('patients_cleaned.csv', index=False)
print("File hasil pembersihan disimpan: patients_cleaned.csv")