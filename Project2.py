import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime  # Add this line for the datetime module

# Function to read Excel file with proper path handling
def read_excel_file(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        st.error(f"Error: File not found at {file_path}. Please check the file path.")
        return None

# Determine file path based on environment (local or Colab-style)
file_path = "Adidas.xlsx"  # Local path
if not os.path.exists(file_path):
    # If the file is not found in the local path, provide the correct path
    st.error("Error: Excel file not found. Please check the file path.")
    df = None
else:
    # Reading the data from the Excel file
    df = read_excel_file(file_path)

# Check if df is not None before further processing
if df is not None:
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

    html_title = """
        <style>
        .title-test {
        font-weight:bold;
        padding:5px;
        border-radius:6px;
        }
        </style>
        <center><h1 class="title-test">Adidas Interactive Sales Dashboard</h1></center>"""

    col3, col4, col5 = st.columns([0.45, 0.45, 0.45])
    with col3:
        box_date=df['InvoiceDate']
        st.write(f"Last updated by:  \n {box_date}")
        # Check if necessary columns are present and not empty
        if 'Retailer' in df.columns and 'TotalSales' in df.columns and not df[['Retailer', 'TotalSales']].empty:
            fig = px.bar(df, x="Retailer", y="TotalSales", labels={"TotalSales": "Total Sales {$}"},
                         title="Total Sales by Retailer", hover_data=["TotalSales"],
                         template="gridon", height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Insufficient data to generate bar chart.")

    _, view1, dwn1, view2, dwn2 = st.columns([0.15, 0.20, 0.20, 0.20, 0.20])
    with view1:
        if 'Retailer' in df.columns and 'TotalSales' in df.columns and not df[['Retailer', 'TotalSales']].empty:
            expander = st.expander("Retailer wise Sales")
            data = df[["Retailer", "TotalSales"]].groupby(by="Retailer")["TotalSales"].sum()
            expander.write(data)
        else:
            st.warning("Insufficient data to display Retailer wise Sales.")
    with dwn1:
        if 'Retailer' in df.columns and 'TotalSales' in df.columns and not df[['Retailer', 'TotalSales']].empty:
            st.download_button("Get Data", data=data.to_csv().encode("utf-8"),
                               file_name="RetailerSales.csv", mime="text/csv")
        else:
            st.warning("Insufficient data to download Retailer wise Sales data.")

df["Month_Year"] = df["InvoiceDate"].dt.strftime("%b'%y'")
result = df.groupby(by=df["Month_Year"])["TotalSales"].sum().reset_index()

with col5:
    fig1 = px.line(result, x="Month_Year", y="TotalSales", title="Total Sales Over Time",
                   template="gridon")
    st.plotly_chart(fig1, use_container_width=True)

with view2:
    expander = st.expander("Monthly Sales")
    data = result
    expander.write(data)
with dwn2:
    st.download_button("Get Data", data=result.to_csv().encode("utf-8"),
                       file_name="Monthly Sales.csv", mime="text/csv")

result1 = df.groupby(by="State")[["TotalSales", "UnitsSold"]].sum().reset_index()

# add the units sold as a line chart on a secondary y-axis
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=result1["State"], y=result1["TotalSales"], name="Total Sales"))
fig3.add_trace(go.Scatter(x=result1["State"], y=result1["UnitsSold"], mode="lines",
                          name="Units Sold", yaxis="y2"))
fig3.update_layout(
    title="Total Sales and Units Sold by State",
    xaxis=dict(title="State"),
    yaxis=dict(title="Total Sales", showgrid=False),
    yaxis2=dict(title="Units Sold", overlaying="y", side="right"),
    template="gridon",
    legend=dict(x=1, y=1.1)
)

_, col6 = st.columns([0.1, 1])
with col6:
    st.plotly_chart(fig3, use_container_width=True)

_, view3, dwn3 = st.columns([0.5, 0.45, 0.45])
with view3:
    expander = st.expander("View Data for Sales by Units Sold")
    expander.write(result1)
with dwn3:
    st.download_button("Get Data", data=result1.to_csv().encode("utf-8"),
                       file_name="Sales_by_UnitsSold.csv", mime="text/csv")
st.divider()

_, col7 = st.columns([0.1, 1])
treemap = df[["Region", "City", "TotalSales"]].groupby(by=["Region", "City"])["TotalSales"].sum().reset_index()


def format_sales(value):
    if value >= 0:
        return '{:.2f} Lakh'.format(value / 1_000_00)


treemap["TotalSales (Formatted)"] = treemap["TotalSales"].apply(format_sales)

fig4 = px.treemap(treemap, path=["Region", "City"], values="TotalSales",
                  hover_name="TotalSales (Formatted)",
                  hover_data=["TotalSales (Formatted)"],
                  color="City", height=700, width=600)
fig4.update_traces(textinfo="label+value")

with col7:
    st.subheader(":point_right: Total Sales by Region and City in Treemap")
    st.plotly_chart(fig4, use_container_width=True)

_, view4, dwn4 = st.columns([0.5, 0.45, 0.45])
with view4:
    result2 = df[["Region", "City", "TotalSales"]].groupby(by=["Region", "City"])["TotalSales"].sum()
    expander = st.expander("View data for Total Sales by Region and City")
    expander.write(result2)
with dwn4:
    st.download_button("Get Data", data=result2.to_csv().encode("utf-8"),
                       file_name="Sales_by_Region.csv", mime="text.csv")

_, view5, dwn5 = st.columns([0.5, 0.45, 0.45])
with view5:
    expander = st.expander("View Sales Raw Data")
    expander.write(df)
with dwn5:
    st.download_button("Get Raw Data", data=df.to_csv().encode("utf-8"),
                       file_name="SalesRawData.csv", mime="text/csv")
st.divider()