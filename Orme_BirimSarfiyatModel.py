import streamlit as st
import pandas as pd

# Sayfa yapılandırması
st.set_page_config(page_title="Tekstil Metraj Hesaplama", layout="wide")

st.title("✂️ Masaüstü Acil Metraj Hesaplama Uygulaması")

# --- KALICI AÇIKLAMALAR BÖLÜMÜ ---
# Bu alan uygulamanın en üstünde her zaman görünür kalır.
st.info("""
**📌 Ölçü Alma Talimatları (Hesaplamadan Önce Ekleyiniz):**
* **BEDEN:** En: Baldır genişliği + 3 cm | Boy: İç boy + Ön ağ + 3 cm
* **KEMER:** En: Bel genişliği gergin + 3 cm | Boy: Kemer yüksekliği * 2 + 3 cm
* **CEP:** En: Cep eni + 3 cm | Boy: Otomat yüksekliği
""")

# --- Yan Menü (Global Parametreler) ---
st.sidebar.header("Genel Ayarlar")
kumas_en = st.sidebar.number_input("Kumaş Eni (cm)", value=140.0, step=1.0)
en_cekme = st.sidebar.number_input("En Çekme (%)", value=1.5, step=0.1)
boy_cekme = st.sidebar.number_input("Boy Çekme (%)", value=1.5, step=0.1)

# Eğer uygulama güncellenmezse veriyi sıfırlamak için bir buton
if st.sidebar.button("Tabloyu ve Verileri Sıfırla"):
    st.session_state.data = pd.DataFrame([
        {"Tür": "Beden", "Adet": 4, "Parça En": 39.0, "Parça Boy": 110.0},
        {"Tür": "Kemer", "Adet": 1, "Parça En": 102.0, "Parça Boy": 11.0},
        {"Tür": "Cep", "Adet": 2, "Parça En": 0.0, "Parça Boy": 0.0},
    ])
    st.rerun()

# --- Veri Giriş Alanı ---
st.subheader("Parça Listesi")

# Başlangıç verisi (Kod ilk çalıştığında bu tablo yüklenir)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"Tür": "Beden", "Adet": 4, "Parça En": 39.0, "Parça Boy": 110.0},
        {"Tür": "Kemer", "Adet": 1, "Parça En": 102.0, "Parça Boy": 11.0},
        {"Tür": "Cep", "Adet": 2, "Parça En": 0.0, "Parça Boy": 0.0},
    ])

# Düzenlenebilir tablo
edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Tür": st.column_config.SelectboxColumn(
            "Parça Türü",
            options=["Beden", "Kemer", "Cep", "Yan Cep", "Kapak", "Astar"],
            help="Parça tipini seçiniz"
        ),
        "Adet": st.column_config.NumberColumn("Adet", min_value=0),
        "Parça En": st.column_config.NumberColumn(
            "Parça En (cm)", 
            help="BEDEN: Baldır+3 | KEMER: Bel+3 | CEP: Cep eni+3"
        ),
        "Parça Boy": st.column_config.NumberColumn(
            "Parça Boy (cm)", 
            help="BEDEN: İç boy+Ön ağ+3 | KEMER: Yükseklik*2+3 | CEP: Otomat Yükseklik"
        ),
    }
)

# --- Hesaplamalar ---
def calculate_metrics(df, k_en, e_cekme, b_cekme):
    calc_df = df.copy()
    if not calc_df.empty:
        # Çekmeli hesaplamalar (Excel formülünüzle birebir aynı)
        calc_df['Çekmeli Boy'] = calc_df['Parça En'] / (1 - (b_cekme / 100))
        calc_df['Çekmeli En'] = calc_df['Parça Boy'] / (1 - (e_cekme / 100))
        # Birim Metraj = (Adet * Çekmeli Boy * Çekmeli En) / Kumaş En
        calc_df['Birim Metraj'] = (calc_df['Adet'] * calc_df['Çekmeli Boy'] * calc_df['Çekmeli En']) / k_en
    return calc_df

result_df = calculate_metrics(edited_df, kumas_en, en_cekme, boy_cekme)

# --- Sonuç Ekranı ---
st.divider()
st.subheader("Hesaplama Sonuçları")

st.dataframe(
    result_df.style.format({
        'Çekmeli Boy': '{:.2f}',
        'Çekmeli En': '{:.2f}',
        'Birim Metraj': '{:.4f}'
    }),
    use_container_width=True
)

toplam_metraj = result_df['Birim Metraj'].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="TOPLAM BİRİM METRAJ", value=f"{toplam_metraj:.2f} cm")
with col2:
    st.metric(label="METRE CİNSİNDEN (Toplam)", value=f"{toplam_metraj/100:.4f} m")

# Alt Bilgi
st.caption("💡 Satır silmek için: Sol baştaki boşluğa tıklayıp satırı seçin ve klavyeden 'Delete' tuşuna basın.")
