import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Kalkulator MTTR & MTBF")

st.title("Kalkulator MTTR (Mean Time To Repair) & MTBF (Mean Time Between Failures)")

st.write("""
Aplikasi ini membantu Anda menghitung MTTR dan MTBF berdasarkan data kegagalan.
Silakan masukkan data kegagalan di bawah ini.
""")

# Bagian Input Data
st.header("1. Input Data Kegagalan")

# Menggunakan expander untuk input manual
with st.expander("Input Data Manual"):
    num_failures = st.number_input("Berapa banyak data kegagalan yang ingin Anda masukkan?", min_value=1, value=1)

    failure_data = []
    for i in range(num_failures):
        st.subheader(f"Data Kegagalan #{i+1}")
        col1, col2 = st.columns(2)
        with col1:
            failure_time_str = st.text_input(f"Waktu Mulai Kegagalan (YYYY-MM-DD HH:MM:SS) #{i+1}", key=f"start_{i}")
        with col2:
            repair_time_str = st.text_input(f"Waktu Selesai Perbaikan (YYYY-MM-DD HH:MM:SS) #{i+1}", key=f"end_{i}")

        try:
            if failure_time_str and repair_time_str:
                failure_time = datetime.strptime(failure_time_str, '%Y-%m-%d %H:%M:%S')
                repair_time = datetime.strptime(repair_time_str, '%Y-%m-%d %H: %M:%S')
                failure_data.append({"Start Time": failure_time, "End Time": repair_time})
        except ValueError:
            st.warning(f"Format tanggal/waktu tidak valid untuk kegagalan #{i+1}. Harap gunakan YYYY-MM-DD HH:MM:SS.")

# Menggunakan file upload untuk data CSV
st.subheader("Atau, Unggah File CSV")
uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])

df = pd.DataFrame(failure_data)

if uploaded_file is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        # Asumsi kolom di CSV bernama 'Start Time' dan 'End Time'
        df_uploaded['Start Time'] = pd.to_datetime(df_uploaded['Start Time'])
        df_uploaded['End Time'] = pd.to_datetime(df_uploaded['End Time'])
        df = pd.concat([df, df_uploaded], ignore_index=True)
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file CSV: {e}")

if not df.empty:
    st.subheader("Data Kegagalan yang Dimasukkan:")
    st.dataframe(df)

    # Perhitungan MTTR
    df['Repair Time'] = (df['End Time'] - df['Start Time']).dt.total_seconds() / 3600 # dalam jam
    total_repair_time = df['Repair Time'].sum()
    num_failures_actual = len(df)

    if num_failures_actual > 0:
        mttr = total_repair_time / num_failures_actual
        st.subheader("2. Hasil Perhitungan MTTR")
        st.metric(label="MTTR (Mean Time To Repair)", value=f"{mttr:.2f} Jam")
        st.write("MTTR adalah waktu rata-rata yang dibutuhkan untuk memperbaiki sistem yang gagal.")
    else:
        st.warning("Tidak ada data kegagalan yang valid untuk menghitung MTTR.")

    # Perhitungan MTBF
    if num_failures_actual > 1:
        # Waktu operasional total = (Waktu terakhir selesai perbaikan) - (Waktu pertama mulai kegagalan)
        # Dikurangi total waktu perbaikan
        total_uptime_period_seconds = (df['End Time'].max() - df['Start Time'].min()).total_seconds()
        total_repair_time_seconds = df['Repair Time'].sum() * 3600 # Ubah kembali ke detik
        
        total_operational_time_seconds = total_uptime_period_seconds - total_repair_time_seconds
        
        # MTBF = Total Waktu Operasional / (Jumlah Kegagalan - 1)
        # Jika Anda memiliki N kegagalan, ada N-1 interval antar kegagalan.
        mtbf = total_operational_time_seconds / (num_failures_actual - 1) / 3600 # dalam jam
        
        st.subheader("3. Hasil Perhitungan MTBF")
        st.metric(label="MTBF (Mean Time Between Failures)", value=f"{mtbf:.2f} Jam")
        st.write("MTBF adalah waktu rata-rata yang diharapkan antara dua kegagalan berturut-turut dalam sistem.")
        st.write(f"Total waktu operasional yang dihitung: {total_operational_time_seconds / 3600:.2f} Jam")
    elif num_failures_actual == 1:
        st.info("Diperlukan setidaknya dua data kegagalan untuk menghitung MTBF.")
    else:
        st.warning("Tidak ada data kegagalan yang valid untuk menghitung MTBF.")

else:
    st.info("Silakan masukkan data kegagalan secara manual atau unggah file CSV untuk memulai perhitungan.")

st.markdown("---")
st.markdown("Dibuat dengan ❤️ menggunakan Streamlit")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            