import streamlit as st
import pandas as pd

# Sayfa yapılandırması
st.set_page_config(page_title="Tekstil Metraj Hesaplama", layout="wide")

st.title("✂️ Masaüstü Acil Metraj Hesaplama Uygulaması")
st.write("Excel dosyanızdaki hesaplama mantığına göre hazırlanmıştır.")

# --- Yan Menü (Global Parametreler) ---
st.sidebar.header("Genel Ayarlar")
kumas_en = st.sidebar.number_input("Kumaş Eni (cm)", value=140.0, step=1.0)
en_cekme = st.sidebar.number_input("En Çekme (%)", value=1.5, step=0.1)
boy_cekme = st.sidebar.number_input("Boy Çekme (%)", value=1.5, step=0.1)

# --- Veri Giriş Alanı ---
st.subheader("Parça Listesi")
st.info("Tabloya yeni satır ekleyebilir, değerleri doğrudan düzenleyebilirsiniz.")

# Başlangıç verisi (Excel'deki örneğe benzer)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"Tür": "Beden", "Adet": 4, "Parça En": 39.0, "Parça Boy": 110.0},
        {"Tür": "Kemer", "Adet": 1, "Parça En": 102.0, "Parça Boy": 11.0},
    ])

# Düzenlenebilir tablo (st.data_editor)
edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Adet": st.column_config.NumberColumn(min_value=0),
        "Parça En": st.column_config.NumberColumn(help="Santimetre cinsinden"),
        "Parça Boy": st.column_config.NumberColumn(help="Santimetre cinsinden"),
    }
)

# --- Hesaplamalar ---
def calculate_metrics(df, k_en, e_cekme, b_cekme):
    # Excel'deki formüllere sadık kalarak:
    # Çekmeli Boy = Parça En / (1 - (Boy Çekme / 100))
    # Çekmeli En = Parça Boy / (1 - (En Çekme / 100))
    # Birim Metraj = (Adet * Çekmeli Boy * Çekmeli En) / Kumaş En
    
    calc_df = df.copy()
    if not calc_df.empty:
        calc_df['Çekmeli Boy'] = calc_df['Parça En'] / (1 - (b_cekme / 100))
        calc_df['Çekmeli En'] = calc_df['Parça Boy'] / (1 - (e_cekme / 100))
        calc_df['Birim Metraj'] = (calc_df['Adet'] * calc_df['Çekmeli Boy'] * calc_df['Çekmeli En']) / k_en
    else:
        calc_df['Çekmeli Boy'] = 0
        calc_df['Çekmeli En'] = 0
        calc_df['Birim Metraj'] = 0
        
    return calc_df

# Sonuçları hesapla
result_df = calculate_metrics(edited_df, kumas_en, en_cekme, boy_cekme)

# --- Sonuç Ekranı ---
st.divider()
st.subheader("Hesaplama Sonuçları")

# Tabloyu göster (Sayıları formatlayarak)
st.dataframe(
    result_df.style.format({
        'Çekmeli Boy': '{:.2f}',
        'Çekmeli En': '{:.2f}',
        'Birim Metraj': '{:.4f}'
    }),
    use_container_width=True
)

# Toplam Metraj Özeti
toplam_metraj = result_df['Birim Metraj'].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="TOPLAM METRAJ", value=f"{toplam_metraj:.2f} cm")
with col2:
    st.metric(label="TOPLAM METRAJ (Metre)", value=f"{toplam_metraj/100:.4f} m")

# --- Export ---
csv = result_df.to_csv(index=False).encode('utf-8')
st.download_button(
    "Sonuçları CSV Olarak İndir",
    csv,
    "maliyet_tablosu.csv",
    "text/csv",
    key='download-csv'
)
