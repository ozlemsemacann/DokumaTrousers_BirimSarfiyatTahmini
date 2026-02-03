import streamlit as st
import pandas as pd

# 1. Sayfa Ayarları
st.set_page_config(page_title="Metraj Hesaplama v2", layout="wide")

# 2. Hafızayı (Session State) Tamamen Sıfırlama Fonksiyonu
def hafizayi_temizle():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

st.title("✂️ Masaüstü Acil Metraj Hesaplama")

# 3. KIRMIZI SIFIRLAMA BUTONU (Eğer değişiklik görmüyorsanız buna basın)
if st.button("⚠️ UYGULAMAYI VE TABLOYU ZORLA SIFIRLA", on_click=hafizayi_temizle):
    st.rerun()

# 4. KALICI AÇIKLAMALAR (Artık info kutusu içinde)
st.success("""
**📏 Ölçü Formülleri:**
* **BEDEN:** En: Baldır genişliği + 3 cm | Boy: İç boy + Ön ağ + 5 cm
* **KEMER:** En: Bel gergin*2 + 3 cm | Boy: Kemer yükseklik * 2 + 3 cm
* **CEP:** En: Cep eni + 3 cm | Boy: Fleto ise Otomat yüksekliği, değilse Cep boyu
""")

# 5. Yan Menü Ayarları
st.sidebar.header("⚙️ Hesaplama Ayarları")
k_en = st.sidebar.number_input("Kumaş Eni (cm)", value=140.0, key="k_en")
e_cek = st.sidebar.number_input("En Çekme (%)", value=1.5, key="e_cek")
b_cek = st.sidebar.number_input("Boy Çekme (%)", value=1.5, key="b_cek")

# 6. Tablo Başlangıç Verisi
initial_data = [
    {"Tür": "Beden", "Adet": 4, "Parça En": 39.0, "Parça Boy": 110.0},
    {"Tür": "Kemer", "Adet": 1, "Parça En": 102.0, "Parça Boy": 11.0},
    {"Tür": "Cep", "Adet": 2, "Parça En": 0.0, "Parça Boy": 0.0},
]

if 'main_table' not in st.session_state:
    st.session_state.main_table = pd.DataFrame(initial_data)

# 7. Düzenlenebilir Tablo
st.subheader("📋 Parça Listesi Düzenleme")
edited_df = st.data_editor(
    st.session_state.main_table,
    num_rows="dynamic",
    use_container_width=True,
    key="editor",
    column_config={
        "Tür": st.column_config.SelectboxColumn("Tür", options=["Beden", "Kemer", "Cep", "Kapak", "Astar"]),
        "Parça En": st.column_config.NumberColumn("Parça En (cm)", help="Baldır+3 / Bel+3 / Cep+3"),
        "Parça Boy": st.column_config.NumberColumn("Parça Boy (cm)", help="İç Boy+Ön Ağ+3 / Kemer*2+3 / Otomat")
    }
)

# 8. Hesaplama Motoru
def hesapla(df):
    d = df.copy()
    if not d.empty:
        d['Çekmeli Boy'] = d['Parça En'] / (1 - (b_cek / 100))
        d['Çekmeli En'] = d['Parça Boy'] / (1 - (e_cek / 100))
        d['Birim Metraj'] = (d['Adet'] * d['Çekmeli Boy'] * d['Çekmeli En']) / k_en
        return d
    return d

res_df = hesapla(edited_df)

# 9. Sonuçlar
st.divider()
st.subheader("📊 Hesaplama Sonuçları")
st.dataframe(res_df, use_container_width=True)

toplam = res_df['Birim Metraj'].sum()

st.metric("TOPLAM METRAJ (Metre)", f"{toplam/100:.4f} m")

