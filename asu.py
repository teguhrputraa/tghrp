import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Konfigurasi halaman Streamlit
st.set_page_config(layout="wide", page_title="Kalkulator MTTR & MTBF")

st.title("Kalkulator MTTR (Mean Time To Repair) & MTBF (Mean Time Between Failures)")

st.write("""
Aplikasi ini membantu Anda menghitung MTTR dan MTBF berdasarkan data kegagalan.
Silakan masukkan data kegagalan di bawah ini, baik secara manual maupun dengan mengunggah file CSV.
""")

# --- Bagian Input Data ---
st.header("1. Input Data Kegagalan")

# Inisialisasi daftar untuk menyimpan data kegagalan manual
manual_failure_data = []

# Menggunakan expander untuk input manual
with st.expander("Input Data Manual"):
    # Input jumlah data kegagalan yang ingin dimasukkan
    num_failures = st.number_input("Berapa banyak data kegagalan yang ingin Anda masukkan?", min_value=1, value=1, key="num_failures_input")

    # Loop untuk input setiap data kegagalan
    for i in range(num_failures):
        st.subheader(f"Data Kegagalan #{i+1}")
        col1, col2 = st.columns(2)
        
        with col1:
            # Input waktu mulai kegagalan
            # Placeholder memberikan contoh format
            failure_time_str = st.text_input(
                f"Waktu Mulai Kegagalan (YYYY-MM-DD HH:MM:SS) #{i+1}", 
                value="", # Biarkan kosong secara default
                placeholder="Contoh: 2024-01-01 10:00:00", 
                key=f"start_time_{i}"
            )
        with col2:
            # Input waktu selesai perbaikan
            repair_time_str = st.text_input(
                f"Waktu Selesai Perbaikan (YYYY-MM-DD HH:MM:SS) #{i+1}", 
                value="", 
                placeholder="Contoh: 2024-01-01 10:30:00", 
                key=f"end_time_{i}"
            )

        # Coba parse input tanggal/waktu
        if failure_time_str and repair_time_str:
            try:
                failure_time = datetime.strptime(failure_time_str, '%Y-%m-%d %H:%M:%S')
                # BUG FIX: Pastikan tidak ada spasi ekstra di format string
                repair_time = datetime.strptime(repair_time_str, '%Y-%m-%d %H:%M:%S') 
                
                # Validasi: Waktu perbaikan harus setelah waktu kegagalan
                if repair_time < failure_time:
                    st.error(f"Error: Waktu Selesai Perbaikan #{i+1} tidak boleh sebelum Waktu Mulai Kegagalan.")
                else:
                    manual_failure_data.append({"Start Time": failure_time, "End Time": repair_time})
            except ValueError:
                st.warning(f"Format tanggal/waktu tidak valid untuk kegagalan #{i+1}. Harap gunakan YYYY-MM-DD HH:MM:SS.")
            except Exception as e:
                st.error(f"Terjadi kesalahan tak terduga saat memproses kegagalan #{i+1}: {e}")

# Membuat DataFrame dari data manual
df_manual = pd.DataFrame(manual_failure_data)

# Menggunakan file upload untuk data CSV
st.subheader("Atau, Unggah File CSV")
uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])

df_uploaded = pd.DataFrame()
if uploaded_file is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        # Memastikan kolom yang ada di CSV sesuai dan mengonversinya ke datetime
        if 'Start Time' in df_uploaded.columns and 'End Time' in df_uploaded.columns:
            df_uploaded['Start Time'] = pd.to_datetime(df_uploaded['Start Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            df_uploaded['End Time'] = pd.to_datetime(df_uploaded['End Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            
            # Hapus baris dengan nilai NaT (Not a Time) jika parsing gagal
            df_uploaded.dropna(subset=['Start Time', 'End Time'], inplace=True)

            # Validasi: Waktu perbaikan harus setelah waktu kegagalan untuk data CSV
            df_uploaded = df_uploaded[df_uploaded['End Time'] >= df_uploaded['Start Time']]

            if df_uploaded.empty:
                st.warning("Tidak ada data yang valid di file CSV setelah filtering (periksa format waktu atau urutan waktu).")

        else:
            st.error("File CSV harus memiliki kolom 'Start Time' dan 'End Time'.")
            df_uploaded = pd.DataFrame() # Kosongkan df_uploaded jika kolom tidak sesuai
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca atau memproses file CSV: {e}")
        df_uploaded = pd.DataFrame() # Kosongkan df_uploaded jika ada error

# Gabungkan data manual dan data dari CSV
df = pd.concat([df_manual, df_uploaded], ignore_index=True)

# Hapus duplikat berdasarkan Start Time dan End Time jika ada
df.drop_duplicates(subset=['Start Time', 'End Time'], inplace=True)
df.sort_values(by='Start Time', inplace=True) # Urutkan berdasarkan waktu mulai kegagalan

# --- Tampilan Data dan Perhitungan ---
if not df.empty:
    st.subheader("Data Kegagalan yang Digunakan untuk Perhitungan:")
    st.dataframe(df)

    # --- Perhitungan MTTR ---
    df['Repair Time'] = (df['End Time'] - df['Start Time']).dt.total_seconds() / 3600 # dalam jam
    total_repair_time = df['Repair Time'].sum()
    num_failures_actual = len(df)

    if num_failures_actual > 0:
        mttr = total_repair_time / num_failures_actual
        st.subheader("2. Hasil Perhitungan MTTR")
        st.metric(label="MTTR (Mean Time To Repair)", value=f"{mttr:.2f} Jam")
        st.write(f"Diambil dari total {total_repair_time:.2f} jam perbaikan dibagi dengan {num_failures_actual} kegagalan.")
        st.write("MTTR adalah waktu rata-rata yang dibutuhkan untuk memperbaiki sistem yang gagal.")
    else:
        st.warning("Tidak ada data kegagalan yang valid untuk menghitung MTTR.")

    # --- Perhitungan MTBF ---
    if num_failures_actual > 1:
        # Untuk MTBF, kita perlu total waktu operasional (uptime)
        # Total durasi periode observasi = (Waktu terakhir selesai perbaikan) - (Waktu pertama mulai kegagalan)
        observation_period_seconds = (df['End Time'].max() - df['Start Time'].min()).total_seconds()
        
        # Total waktu perbaikan dalam detik
        total_repair_time_seconds = df['Repair Time'].sum() * 3600 
        
        # Total waktu operasional = Total durasi periode - Total waktu perbaikan
        total_operational_time_seconds = observation_period_seconds - total_repair_time_seconds
        
        # Pastikan waktu operasional tidak negatif (bisa terjadi jika data aneh)
        if total_operational_time_seconds < 0:
            st.error("Perhitungan waktu operasional menghasilkan nilai negatif. Mohon periksa data kegagalan Anda (misalnya, tumpang tindih waktu perbaikan atau durasi perbaikan yang sangat panjang).")
            mtbf = 0 # Atau tangani sesuai kebutuhan
        else:
            # MTBF = Total Waktu Operasional / (Jumlah Kegagalan - 1)
            # Karena ada N kegagalan, ada N-1 interval antar kegagalan.
            mtbf = total_operational_time_seconds / (num_failures_actual - 1) / 3600 # dalam jam
            
            st.subheader("3. Hasil Perhitungan MTBF")
            st.metric(label="MTBF (Mean Time Between Failures)", value=f"{mtbf:.2f} Jam")
            st.write(f"Diambil dari total {total_operational_time_seconds / 3600:.2f} jam waktu operasional dibagi dengan {num_failures_actual - 1} interval antar kegagalan.")
            st.write("MTBF adalah waktu rata-rata yang diharapkan antara dua kegagalan berturut-turut dalam sistem.")
            
            st.info(
                f"**Detail Perhitungan MTBF:**\n"
                f"- Durasi Periode Observasi: {observation_period_seconds / 3600:.2f} Jam (dari kegagalan pertama hingga perbaikan terakhir)\n"
                f"- Total Waktu Perbaikan: {total_repair_time_seconds / 3600:.2f} Jam\n"
                f"- Total Waktu Operasional (Uptime): {total_operational_time_seconds / 3600:.2f} Jam\n"
                f"- Jumlah Interval Kegagalan: {num_failures_actual - 1}"
            )
    elif num_failures_actual == 1:
        st.info("Diperlukan setidaknya dua data kegagalan untuk menghitung MTBF.")
    else:
        st.warning("Tidak ada data kegagalan yang valid untuk menghitung MTBF.")

else:
    st.info("Silakan masukkan data kegagalan secara manual atau unggah file CSV untuk memulai perhitungan.")

st.markdown("---")
st.markdown("Dibuat dengan ❤️ menggunakan Streamlit")
