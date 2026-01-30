
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="CAC vs CLTV Analizi (J-Curve)", layout="wide")

st.title("Net Kârlılık ve Payback Analizi (J-Curve)")
st.markdown("""
Bu grafik, yapılan yatırımın (CAC) zamanla nasıl geri döndüğünü gösterir.
**Kırmızı Bölge:** Yatırım henüz çıkmadı (Zarar).
**Yeşil Bölge:** Yatırım çıktı ve şirket kâra geçti.
""")

# --- SIDEBAR ---
st.sidebar.header("Parametreler")
cac = st.sidebar.number_input("CAC ($)", min_value=10, value=200, step=10)
aov = st.sidebar.number_input("AOV ($)", min_value=1, value=50, step=5)
purchase_freq = st.sidebar.slider("Sıklık (Ayda)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
profit_margin = st.sidebar.slider("Kâr Marjı (%)", min_value=0.05, max_value=1.0, value=0.20, step=0.05)
churn_rate = st.sidebar.slider("Churn Oranı (%)", min_value=0.01, max_value=0.50, value=0.05, step=0.01)

# --- HESAPLAMA (1 YILLIK) ---
# Düzeltme 1: Süre 12 ay (0. ay başlangıç dahil 13 nokta)
months = list(range(13))

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

df = pd.DataFrame({'Ay': months, 'Net Durum': net_values})

# --- PAYBACK BULMA ---
payback_month = next((i for i, val in enumerate(net_values) if val >= 0), None)

# --- RENKLİ J-CURVE GRAFİĞİ ---
fig = go.Figure()

# 0 Çizgisi
fig.add_hline(y=0, line_width=1, line_color="black")

# Düzeltme 2: Renklendirme Mantığı
# Plotly'de tek çizgiyi iki renk yapmak zordur.
# Bu yüzden "0'ın altı" ve "0'ın üstü" diye görsel hile yapıyoruz.

# 1. Ana Çizgi (Nötr Renk - Gri)
fig.add_trace(go.Scatter(
    x=df['Ay'], y=df['Net Durum'],
    mode='lines+markers',
    name='Net Akış',
    line=dict(color='gray', width=2),
    marker=dict(size=6)
))

# 2. Kırmızı Dolgu (Zarar Bölgesi)
# Sadece 0'ın altındaki değerleri çiziyoruz
fig.add_trace(go.Scatter(
    x=df['Ay'],
    y=[val if val <= 0 else 0 for val in df['Net Durum']],  # 0'ın üstündekileri 0'a çek ki taşmasın
    mode='lines',
    name='Zarar Bölgesi',
    line=dict(width=0),  # Çizgisi görünmesin, sadece dolgusu
    fill='tozeroy',
    fillcolor='rgba(255, 0, 0, 0.2)',  # Hafif saydam Kırmızı
    hoverinfo='skip'  # Mouse üzerine gelince bilgi çıkmasın
))

# 3. Yeşil Dolgu (Kâr Bölgesi)
# Sadece 0'ın üstündeki değerleri çiziyoruz
fig.add_trace(go.Scatter(
    x=df['Ay'],
    y=[val if val >= 0 else 0 for val in df['Net Durum']],
    mode='lines',
    name='Kâr Bölgesi',
    line=dict(width=0),
    fill='tozeroy',
    fillcolor='rgba(0, 200, 0, 0.2)',  # Hafif saydam Yeşil
    hoverinfo='skip'
))

# Payback İşaretleyicisi
if payback_month:
    fig.add_vline(x=payback_month, line_dash="dash", line_color="green")
    fig.add_annotation(
        x=payback_month, y=0,
        text=f"Payback: {payback_month}. Ay",
        showarrow=True, arrowhead=2, yshift=20,
        font=dict(color="green", weight="bold")
    )

fig.update_layout(
    title='1 Yıllık Yatırım Geri Dönüş Simülasyonu',
    xaxis_title='Zaman (Ay)',
    yaxis_title='Net Durum ($)',
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# --- METRİKLER ---
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("İlk Yatırım (CAC)", f"${cac}", help="Başlangıç maliyeti")

with col2:
    if payback_month:
        st.metric("Amorti Süresi", f"{payback_month} Ay", delta_color="normal")
    else:
        st.metric("Amorti Süresi", "Dönüş Yok (12+)", delta_color="off")

with col3:
    # Düzeltme 3: ROI Göstergesi
    final_net_value = df.iloc[-1]['Net Durum']
    roi_percent = (final_net_value / cac) * 100

    # Delta parametresine direkt sayıyı veriyoruz, Streamlit rengi (Kırmızı/Yeşil) kendi ayarlar.
    st.metric(
        label="1. Yıl Sonu Net Kâr/Zarar",
        value=f"${final_net_value:.1f}",
        delta=f"{final_net_value:.1f}$"  # Burası negatifse Kırmızı Ok, pozitifse Yeşil Ok olur
    )

if __name__ == "__main__":
    st.caption("Not: Grafik kırmızı alandayken yatırım henüz geri dönmemiştir.")
