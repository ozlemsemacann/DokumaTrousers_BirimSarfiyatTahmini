import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Trousers Metraj v3", layout="wide", page_icon="✂️")

# 2. Google Sheets Bağlantısı
# URL'niz: https://docs.google.com/spreadsheets/d/1A2ayp13KH1EPJqKd7zCOJx9wtR3sxEf4cduLnOD0wCE/edit
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Hafızayı Sıfırlama Fonksiyonu
def hafizayi_temizle():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

st.title("✂️ Trousers Metraj Hesaplama & Kayıt")

# 4. Bilgi Kutusu
st.info("""
**📏 Hesaplama Standartları:**
* Beden: Baldır+3cm / İç boy+Ön ağ+5cm
* Kemer: Bel*2+3cm / Yükseklik*2+3cm
""")

# 5. Yan Menü Parametreleri
st.sidebar.header("⚙️ Parametreler")
k_en = st.sidebar.number_input("Kumaş Eni (cm)", value=140.0)
e_cek = st.sidebar.number_input("En Çekme (%)", value=1.5)
b_cek = st.sidebar.number_input("Boy Çekme (%)", value=1.5)

if st.sidebar.button("🔄 Tüm Sayfayı Sıfırla"):
    hafizayi_temizle()

# 6. Tablo Başlangıç Verisi
initial_data = [
    {"Tür": "Beden", "Adet": 4, "Parça En": 39.0, "Parça Boy": 110.0},
    {"Tür": "Kemer", "Adet": 1, "Parça En": 102.0, "Parça Boy": 11.0},
    {"Tür": "Cep", "Adet": 2, "Parça En": 25.0, "Parça Boy": 30.0},
]

if 'main_table' not in st.session_state:
    st.session_state.main_table = pd.DataFrame(initial_data)

# 7. Düzenlenebilir Tablo
st.subheader("📋 Parça Listesi")
edited_df = st.data_editor(
    st.session_state.main_table, 
    num_rows="dynamic", 
    use_container_width=True,
    key="table_editor"
)

# 8. Hesaplama Motoru
def hesapla(df):
    d = df.copy()
    if not d.empty:
        # Formül: (Adet * (Boy/(1-BoyÇekme)) * (En/(1-EnÇekme))) / KumaşEni
        d['Çekmeli Boy'] = d['Parça Boy'] / (1 - (b_cek / 100))
        d['Çekmeli En'] = d['Parça En'] / (1 - (e_cek / 100))
        d['Birim Metraj'] = (d['Adet'] * d['Çekmeli Boy'] * d['Çekmeli En']) / k_en
        return d
    return d

res_df = hesapla(edited_df)
toplam_metraj = res_df['Birim Metraj'].sum() / 100 # cm'den metreye çevrim

# 9. Sonuç Paneli
st.divider()
c1, c2 = st.columns([3, 1])
with c1:
    st.dataframe(res_df[['Tür', 'Adet', 'Parça En', 'Parça Boy', 'Birim Metraj']], use_container_width=True)
with c2:
    st.metric("TOPLAM (Metre)", f"{toplam_metraj:.4f} m")

# 10. Google Sheets Kayıt İşlemi
st.subheader("💾 Kayıt Yönetimi")
if st.button("🚀 Hesaplamayı Google Sheets'e Gönder", type="primary"):
    try:
        # Mevcut veriyi çek
        url = "https://docs.google.com/spreadsheets/d/1A2ayp13KH1EPJqKd7zCOJx9wtR3sxEf4cduLnOD0wCE/edit#gid=0"
        existing_data = conn.read(spreadsheet=url, usecols=list(range(7))) # İlk 7 sütunu oku
        
        # Yeni satırı hazırla
        new_row = pd.DataFrame([{
            "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Kumas_En": k_en,
            "En_Cekme": e_cek,
            "Boy_Cekme": b_cek,
            "Toplam_Metraj": round(toplam_metraj, 4),
            "Detaylar": str(edited_df['Tür'].tolist())
        }])
        
        # Veriyi birleştir
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        
        # Güncelle
        conn.update(spreadsheet=url, data=updated_df)
        st.success("Veriler başarıyla Google Sheets'e eklendi!")
    except Exception as e:
        st.error(f"Hata: {e}")
        st.warning("Not: Google Sheet dosyanızın 'Düzenleyebilir' olarak paylaşıldığından emin olun.")

# 11. Arşiv Görüntüleme
with st.expander("📂 Kayıt Geçmişini Görüntüle"):
    if st.button("Verileri Yenile"):
        st.rerun()
    history = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/1A2ayp13KH1EPJqKd7zCOJx9wtR3sxEf4cduLnOD0wCE/edit#gid=0")
    st.dataframe(history, use_container_width=True)
