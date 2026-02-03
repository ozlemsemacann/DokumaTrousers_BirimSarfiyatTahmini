import streamlit as st
import pandas as pd

# Sayfa yapılandırması
st.set_page_config(page_title="Tekstil Metraj Hesaplama", layout="wide")

st.title("✂️ Masaüstü Acil Metraj Hesaplama Uygulaması")

# --- KALICI AÇIKLAMALAR BÖLÜMÜ ---
st.info("""
**📌 Parça Ölçü Notları (Kalıcı Açıklama):**
* **BEDEN:** En: Baldır genişliği + 3 cm ekle | Boy: İç boy + Ön ağ + 3 cm ekle
* **KEMER:** En: Bel genişliği gergin + 3 cm ekle | Boy: Kemer yüksekliği * 2 cm + 3 cm ekle
* **CEP:** En: Cep eni + 3 cm ekle | Boy: Otomat yüksekliği
""")

# --- Yan Menü (Global Parametreler) ---
st.sidebar.header("Genel Ayarlar")
kumas_en = st.sidebar.number_input("Kumaş Eni (cm)", value=140.0, step=1.0)
en_cekme = st.sidebar.number_input("En Çekme (%)", value=1.5, step=0.1)
boy_cekme = st.sidebar.number_input("Boy Çekme (%)", value=1.5, step=0.1)

# --- Veri Giriş Alanı ---
st.subheader("Parça Listesi")

# Başlangıç verisi (Beden, Kemer ve istediğiniz Cep satırı eklendi)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"Tür": "Beden", "Adet": 4, "Parça En": 39.0, "Parça Boy": 110.0},
        {"Tür": "Kemer", "Adet": 1, "Parça En": 102.0, "Parça Boy": 11.0},
        {"Tür": "Cep", "Adet": 2, "Parça En": 0.0, "Parça Boy": 0.0}, # Yeni Cep Satırı
    ])

# Düzenlenebilir tablo
# column_config ile başlıkların üzerine gelindiğinde açıklamaların görünmesini sağladık
edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Tür": st.column_config.SelectboxColumn(
            "Parça Türü",
            options=["Beden", "Kemer", "Cep", "Yan Cep", "Kapak", "Diğer"],
            help="Beden, Kemer veya Cep seçiniz."
        ),
        "Adet": st.column_config.NumberColumn("Adet", min_value=0),
        "Parça En": st.column_config.NumberColumn(
            "Parça En (cm)", 
            help="Beden: Baldır+3 | Kemer: Bel+3 | Cep: Cep eni+3"
        ),
        "Parça Boy": st.column_config.NumberColumn(
            "Parça Boy (cm)", 
            help="Beden: İç boy+Ön ağ+3 | Kemer: Yükseklik*2+3 | Cep: Otomat Yükseklik"
        ),
    }
)

# --- Hesaplamalar ---
def calculate_metrics(df, k_en, e_cekme, b_cekme):
    calc_df = df.copy()
    if not calc_df.empty:
        # Excel formülleri:
        calc_df['Çekmeli Boy'] = calc_df['Parça En'] / (1 - (b_cekme / 100))
        calc_df['Çekmeli En'] = calc_df['Parça Boy'] / (1 - (e_cekme / 100))
        calc_df['Birim Metraj'] = (calc_df['Adet'] * calc_df
