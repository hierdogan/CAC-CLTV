import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- AYARLAR ---
# Bu komut her zaman en başta olmalı
st.set_page_config(page_title="Growth Analiz Platformu", layout="wide")


# --- ORTAK HESAPLAMA MOTORU ---
# Bu fonksiyonu her iki sayfa da kullanacak. Kod tekrarını önlüyoruz.
def hesapla_senaryo(cac, aov, purchase_freq, profit_margin, churn_rate):
    months = list(range(13))  # 1 Yıllık
    net_values = []
    current_customers = 1.0
    cumulative_profit = 0

    for m in months:
        if m == 0:
            net_values.append(-cac)
        else:
            monthly_profit = (aov * purchase_freq * profit_margin) * current_customers
            cumulative_profit += monthly_profit
            net_values.append(cumulative_profit - cac)
            current_customers = current_customers * (1 - churn_rate)

    # Payback ayını bul
    payback = next((i for i, val in enumerate(net_values) if val >= 0), None)

    # Son durum (ROI hesabı için)
    final_val = net_values[-1]
    roi = (final_val / cac) * 100

    return months, net_values, payback, final_val, roi


# --- SIDEBAR NAVİGASYON ---
st.sidebar.title("🚀 Analiz Modülleri")
page = st.sidebar.radio(
    "Gitmek istediğiniz sayfayı seçin:",
    ["Tekli J-Curve Analizi", "A/B Senaryo Kıyaslama"]
)

st.sidebar.divider()  # Görsel ayraç

# ==========================================
# SAYFA 1: TEKLİ J-CURVE ANALİZİ (Eski Dostumuz)
# ==========================================
if page == "Tekli J-Curve Analizi":
    st.title("Tekli Yatırım Dönüş Analizi (J-Curve)")
    st.markdown("Bir ürün veya kampanya için yatırımın geri dönüş süresini ve kârlılığını analiz edin.")

    # Parametreler
    st.sidebar.header("Parametreler")
    cac = st.sidebar.number_input("CAC ($)", 10, 500, 200, 10, key="s1_cac")
    aov = st.sidebar.number_input("AOV ($)", 1, 200, 50, 5, key="s1_aov")
    freq = st.sidebar.slider("Sıklık (Ayda)", 0.1, 5.0, 1.0, 0.1, key="s1_freq")
    margin = st.sidebar.slider("Kâr Marjı (%)", 0.05, 1.0, 0.20, 0.05, key="s1_margin")
    churn = st.sidebar.slider("Churn (%)", 0.01, 0.50, 0.05, 0.01, key="s1_churn")

    # Hesapla
    months, net_values, payback, final_val, roi = hesapla_senaryo(cac, aov, freq, margin, churn)
    df = pd.DataFrame({'Ay': months, 'Net Durum': net_values})

    # Grafik (Renkli Dolgulu)
    fig = go.Figure()
    fig.add_hline(y=0, line_color="black", line_width=1)

    # 0'ın altı (Zarar)
    fig.add_trace(go.Scatter(
        x=df['Ay'], y=[val if val <= 0 else 0 for val in df['Net Durum']],
        mode='lines', line=dict(width=0), fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.2)', name='Zarar',
        hoverinfo='skip'
    ))
    # 0'ın üstü (Kâr)
    fig.add_trace(go.Scatter(
        x=df['Ay'], y=[val if val >= 0 else 0 for val in df['Net Durum']],
        mode='lines', line=dict(width=0), fill='tozeroy', fillcolor='rgba(0, 200, 0, 0.2)', name='Kâr', hoverinfo='skip'
    ))
    # Ana Çizgi
    fig.add_trace(
        go.Scatter(x=df['Ay'], y=df['Net Durum'], mode='lines+markers', name='Net Akış', line=dict(color='gray')))

    # Payback İşaretleyicisi
    if payback:
        fig.add_vline(x=payback, line_dash="dash", line_color="green")
        fig.add_annotation(x=payback, y=0, text=f"Payback: {payback}. Ay", showarrow=True, arrowhead=2, yshift=20,
                           font=dict(color="green", weight="bold"))

    st.plotly_chart(fig, use_container_width=True)

    # Metrikler
    col1, col2, col3 = st.columns(3)
    col1.metric("İlk Yatırım (CAC)", f"${cac}")
    col2.metric("Amorti Süresi", f"{payback} Ay" if payback else ">12 Ay")
    col3.metric("1. Yıl Sonu Net Durum", f"${final_val:.1f}", delta=f"${final_val:.1f}")

# ==========================================
# SAYFA 2: A/B SENARYO KIYASLAMA (Yeni Özellik)
# ==========================================
elif page == "A/B Senaryo Kıyaslama":
    st.title("⚔️ Strateji Savaşı: Senaryo A vs B")
    st.markdown("İki farklı büyüme stratejisini yan yana kıyaslayın.")

    tab_a, tab_b = st.sidebar.tabs(["Senaryo A (Mevcut)", "Senaryo B (Hedef)"])

    # Senaryo A Girdileri
    with tab_a:
        st.caption("Mevcut Durum")
        cac_a = st.number_input("CAC ($)", 10, 500, 200, key="a_cac")
        aov_a = st.number_input("AOV ($)", 1, 200, 50, key="a_aov")
        freq_a = st.slider("Sıklık", 0.1, 5.0, 1.0, key="a_freq")
        margin_a = st.slider("Kâr Marjı (%)", 0.05, 1.0, 0.20, key="a_margin")
        churn_a = st.slider("Churn (%)", 0.01, 0.50, 0.05, key="a_churn")

    # Senaryo B Girdileri
    with tab_b:
        st.caption("Denemek İstediğin Strateji")
        cac_b = st.number_input("CAC ($)", 10, 500, 250, key="b_cac")
        aov_b = st.number_input("AOV ($)", 1, 200, 60, key="b_aov")
        freq_b = st.slider("Sıklık", 0.1, 5.0, 1.2, key="b_freq")
        margin_b = st.slider("Kâr Marjı (%)", 0.05, 1.0, 0.25, key="b_margin")
        churn_b = st.slider("Churn (%)", 0.01, 0.50, 0.04, key="b_churn")

    # Hesaplamalar
    months, val_a, pay_a, final_a, roi_a = hesapla_senaryo(cac_a, aov_a, freq_a, margin_a, churn_a)
    months, val_b, pay_b, final_b, roi_b = hesapla_senaryo(cac_b, aov_b, freq_b, margin_b, churn_b)

    # Kıyaslama Grafiği
    fig = go.Figure()
    fig.add_hline(y=0, line_color="black", line_width=1)

    fig.add_trace(
        go.Scatter(x=months, y=val_a, mode='lines+markers', name='Senaryo A', line=dict(color='#1f77b4', width=3)))
    fig.add_trace(go.Scatter(x=months, y=val_b, mode='lines+markers', name='Senaryo B',
                             line=dict(color='#ff7f0e', width=3, dash='dash')))

    fig.update_layout(title='Senaryo Karşılaştırması', xaxis_title='Ay', yaxis_title='Net Durum ($)')
    st.plotly_chart(fig, use_container_width=True)

    # Kıyaslama Kartları
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Senaryo B: ROI", f"%{roi_b:.1f}", delta=f"%{roi_b - roi_a:.1f} Fark")
    c2.metric("Senaryo B: Net Kâr", f"${final_b:.1f}", delta=f"${final_b - final_a:.1f} Fark")

    pay_diff = None
    if pay_a and pay_b:
        pay_diff = f"{pay_b - pay_a} Ay"
    c3.metric("Senaryo B: Payback", f"{pay_b} Ay" if pay_b else ">12", delta=pay_diff, delta_color="inverse")