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
                st.error(f"Terjadi kesalahan tak terduga saat memproses keg
