import streamlit as st
import pandas as pd
import io
import plotly.express as px

st.set_page_config(page_title="DSS Iklim Sumsel", layout="wide")

st.title("🌦️ Decision Support System Iklim - Sumatera Selatan")
st.markdown("Mendukung literasi iklim dan berpikir komputasi calon guru fisika melalui analisis data cuaca harian.")

# DSS Functions
def klasifikasi_cuaca(ch, matahari):
    if ch > 20:
        return "Hujan"
    elif ch > 5:
        return "Berawan"
    elif matahari > 4:
        return "Cerah"
    else:
        return "Berawan"

def risiko_kekeringan(ch, matahari):
    if ch < 1 and matahari > 6:
        return "Risiko Tinggi"
    elif ch < 5:
        return "Risiko Sedang"
    else:
        return "Risiko Rendah"

def hujan_ekstrem(ch):
    return "Ya" if ch > 50 else "Tidak"

# Upload Data
st.sidebar.header("⬆️ Upload Data")
uploaded_file = st.sidebar.file_uploader("Unggah file Excel (.xlsx)", type=["xlsx"])

@st.cache_data
def process_data(uploaded_file):
    df = pd.read_excel(uploaded_file, sheet_name="Data Harian - Table")
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], format="%d-%m-%Y")
    df["Prediksi Cuaca"] = df.apply(lambda row: klasifikasi_cuaca(row["curah_hujan"], row["matahari"]), axis=1)
    df["Risiko Kekeringan"] = df.apply(lambda row: risiko_kekeringan(row["curah_hujan"], row["matahari"]), axis=1)
    df["Hujan Ekstrem"] = df["curah_hujan"].apply(hujan_ekstrem)
    return df

# Default or uploaded data
if uploaded_file:
    data = process_data(uploaded_file)
else:
    data = process_data("SUMSEL.xlsx")

# Sidebar: Pilih Tanggal
st.sidebar.header("📅 Filter Tanggal")
tanggal = st.sidebar.date_input("Pilih Tanggal", value=data["Tanggal"].min(), min_value=data["Tanggal"].min(), max_value=data["Tanggal"].max())

# Tampilkan Info Harian
baris = data[data["Tanggal"] == pd.to_datetime(tanggal)]
if not baris.empty:
    info = baris.iloc[0]
    st.subheader(f"📊 Data Iklim - {tanggal.strftime('%d %B %Y')}")
    st.write(f"- Suhu rata-rata: **{info['Tavg']}°C**")
    st.write(f"- Kelembaban: **{info['kelembaban']}%**")
    st.write(f"- Curah hujan: **{info['curah_hujan']} mm**")
    st.write(f"- Matahari: **{info['matahari']} jam**")
    st.write(f"- Kecepatan angin: **{info['kecepatan_angin']} km/jam**")

    st.markdown("---")
    st.subheader("🤖 Hasil Analisis Sistem")
    st.success(f"**Prediksi Cuaca:** {info['Prediksi Cuaca']}")
    st.info(f"**Risiko Kekeringan:** {info['Risiko Kekeringan']}")
    st.warning(f"**Hujan Ekstrem:** {info['Hujan Ekstrem']}")
else:
    st.error("Data tidak ditemukan untuk tanggal tersebut.")

# Grafik Interaktif
st.markdown("---")
st.subheader("📈 Grafik Tren Iklim")

col1, col2 = st.columns(2)

with col1:
    fig_suhu = px.line(data, x="Tanggal", y=["Tn", "Tx", "Tavg"], title="Tren Suhu Harian")
    st.plotly_chart(fig_suhu, use_container_width=True)

with col2:
    fig_hujan = px.line(data, x="Tanggal", y="curah_hujan", title="Tren Curah Hujan Harian")
    st.plotly_chart(fig_hujan, use_container_width=True)

# Tampilkan Data
with st.expander("📁 Lihat dan Unduh Data Lengkap"):
    st.dataframe(data)

    # Export to Excel
    st.markdown("⬇️ **Unduh Data Hasil Analisis:**")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Hasil DSS', index=False)
        writer.close()
    st.download_button(label="Unduh Excel", data=buffer.getvalue(), file_name="hasil_dss_iklim.xlsx", mime="application/vnd.ms-excel")
