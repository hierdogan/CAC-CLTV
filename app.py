# first, we import the necessary libraries

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# We create a fixed dataframe

data = {
'Time': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
'Cost': [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
}

df = pd.DataFrame(data)

st.title("This app created for MIUUL Data Scientist Bootcamp")

# We use Streamlit's slider feature to create a dynamic chart.  For the x and y axes, we set a range at the min and max points using the dataframe

x_min = st.slider("X Eksen Minimum Değeri", min_value=df['Time'].min(), max_value=df['Time'].max(), value=df['Time'].min())
x_max = st.slider("X Eksen Maksimum Değeri", min_value=df['Time'].min(), max_value=df['Time'].max(), value=df['Time'].max())

y_min = st.slider("Y Eksen Minimum Değeri", min_value=df['Cost'].min(), max_value=df['Cost'].max(), value=df['Cost'].min())
y_max = st.slider("Y Eksen Maksimum Değeri", min_value=df['Cost'].min(), max_value=df['Cost'].max(), value=df['Cost'].max())


# Create a dynamic subset DataFrame using the selected x and y ranges:

dynamic_df = df[(df['Time'] >= x_min) & (df['Time'] <= x_max) & (df['Cost'] >= y_min) & (df['Cost'] <= y_max)]


# Create an area chart using a dynamic DataFrame using Plotly Express:
fig = px.area(dynamic_df,
            x='Time',
            y='Cost',
            title="CAC - CLTV Payback",
)
st.plotly_chart(fig)


# We copy the address of the chart in this url and use it in our application. Of course we don't forget to cite the source.
st.header("CAC - CLTV Payback Graph")
st.image("https://images.prismic.io/paddle/b996dd76-f520-4d4d-94e0-c588b2886ebd_CaC_Payback-2.png?auto=compress%2Cformat&fit=max&w=1920")
st.write("Source: [paddle.com](https://www.paddle.com/resources/customer-acquisition-cost)")

if __name__ == "__main__":
    st.title("CLTV Calculation")
    st.write("Average Order Value = Total Price / Total Transaction")
    st.write("Purchase Freq = Total Transaction / Total Number of Customers")
    st.write("Churn = 1 - Repeat Rate")
    st.write("Profit Margin = Total Price * 0.10")
    st.write("Customer Value = Average Order Value * Purchase Freq")
    st.write("CLTV = (Customer Value / Churn) * Profit Margin")