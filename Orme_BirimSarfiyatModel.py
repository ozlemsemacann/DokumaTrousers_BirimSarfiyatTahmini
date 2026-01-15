import streamlit as st
import pandas as pd
from catboost import CatBoostRegressor

# -----------------------------
# Modeli yükle
# -----------------------------
@st.cache_resource
def load_model():
    model = CatBoostRegressor()
    model.load_model("Orme_BirimSarfiyatModel.cbm")
    return model

model = load_model()

# -----------------------------
# Streamlit Arayüzü
# -----------------------------
st.title("🧵 Birim Sarfiyat Tahmini")

st.markdown("Modeli önceden eğittik ve yükledik. Şimdi değerleri gir, tahmini al!")

# Kullanıcıdan girişler
inputs = {}
inputs['Departman'] = st.selectbox("Departman", ['Man'])
inputs['Model_Turu'] = st.selectbox("Model_Turu", ['SWEAT SHIRT','SHORT SLEEVE T-SHIRT'])
inputs['Fit'] = st.selectbox("Fit", ['BOXY_FIT','LOOSE_FIT','REGULAR_FIT','NEW_REGULAR_FIT','RELAX_FIT','OVERSIZE_FIT','COMFORT_FIT','SLIM_FIT','STANDART_FIT','NEW_BOXY'])
inputs['Kalip'] = st.selectbox("Kalip", ['Kalip_Bilgisi_Yok','SL39','CL9','SL14','T27','SL40','SL49','SL2','SL48','SL38','SL41','SL37'])
# Kumaş Eni Değerini 130 ile 176 arasına sınırlama
inputs['Kumas_Eni'] = st.number_input(
    "Kumas_Eni",
    min_value=110.0,
    max_value=200.0,
    value=180.0) # Başlangıç değeri
# Kumaş Gramaji 1 ile 30 arasına sınırlama
inputs['Kumas_Gramaji'] = st.number_input(
    "Kumas_Gramaji",
    min_value=110.0,
    max_value=500.0,
    value=150.0) # Başlangıç değeri
inputs['Pastal_Turu'] = st.selectbox("Pastal_Turu", ['Ana_Beden','Etek_Kol','Yaka','Kol','Etek_Kol_Yaka','Omuz','Kol_Yaka','Kapuson','Cep','Etek'])
inputs['Asorti'] = st.selectbox("Asorti", ['XS(1),S(2),M(3),L(2),XL(1),XXL(1)','XS(1),S(2),M(3),L(3),XL(2),XXL(1),3XL(1)','XS(1),S(2),M(2),L(2),XL(1)','S(2),M(2),L(2),XL(2),XXL(1)','S(4),M(4),L(4),XL(4),XXL(2)','XS(1),S(2),M(2),L(2),XL(2),XXL(1)','XS(2),S(4),M(4),L(4),XL(4),XXL(2)','XS(1),S(1),M(2),L(2),XL(2),XXL(3),3XL(1),4XL(1)','XS(2),S(4),M(6),L(4),XL(2),XXL(2)','XS(4),S(6),M(6),L(6),XL(4)','XS(2),S(3),M(3),L(3),XL(2)','S(2),M(3),L(3),XL(2),XXL(1)','S(1),M(3),L(3),XL(3),XXL(2),3XL(1)','XS(1),S(2),M(3),L(1),XL(1)','XS(1),S(2),M(3),L(2),XL(1)','S(2),M(3),L(2),XL(1)','XS(2),S(2),M(2),L(2),XL(2),XXL(2)','XS(1),S(2),M(3),L(3),XL(2),XXL(1)','XS(1),S(2),M(3),L(3),XL(2),2XL(1),3XL(1)','XS(1),S(2),M(3),L(2),XL(2)','S(1),M(2),L(3),XL(2),XXL(1)','XS(2),S(3),M(3),L(2),XL(1),XXL(1)','XS(2),S(3),M(3),L(2),XL(1)','S(1),M(2),L(2),XL(1)','XS(1),S(2),M(2),L(2),XL(1),XXL(1)','XS(1),S(2),M(2),L(1)','S(2),M(3),L(3),XL(2),2XL(1)','S(1),M(2),L(3),XL(3),XXL(2),3XL(1)','S(2),M(3),L(2),XL(1),XXL(1)','XS(1),S(2),M(3),L(2),XL(2),XXL(1)','S(2),M(3),L(3),XL(2)','XS(1),S(3),M(3),L(2),XL(1)','S(1),M(2),L(2),XL(2),XXL(1)','S(1),M(2),L(2),XL(2),XXL(1),3XL(1)','S(1),M(2),L(2),XL(2),XXL(2)','XS(1),S(2),M(3),L(3),XL(2)','S(1),M(2),L(2),XL(1),XXL(1)','S(1),M(3),L(3),XL(2),XXL(1)','XS(1),S(2),M(3),L(3),XL(1),XXL(1)','XS(1),S(2),M(3),L(2),XL(2),XXL(2),3XL(1)','XS(1),S(2),M(3),L(3),XL(2),XXL(2),3XL(1)','XS(1),S(2),M(3),L(2),XL(2','3XL(6),4XL(4),5XL(2),6XL(1)'])
# Asorti Sayısı Değerini 1 ile 30 arasına sınırlama
inputs['Asorti_Sayisi'] = st.number_input(
    "Asorti_Sayisi",
    min_value=6.0,
    max_value=14.0,
    value=10.0) # Başlangıç değeri
# Parça Sayısı Değerini 1 ile 13 arasına sınırlama
inputs['Parca_Sayisi'] = st.number_input(
    "Parca_Sayisi",
    min_value=1.0,
    max_value=13.0,
    value=4.0) # Başlangıç değeri

# DataFrame oluştur
X_new = pd.DataFrame([inputs])

# Tahmin
if st.button("Tahmin Et"):
    from catboost import Pool

    cat_features = ['Departman', 'Model_Turu', 'Kalip', 'Fit',
                    'Pastal_Turu', 'Asorti']

    X_new_pool = Pool(X_new, cat_features=cat_features)
    prediction = model.predict(X_new_pool)[0]
    st.success(f"🔮 Tahmini Birim Sarfiyat: **{prediction:.2f}**")