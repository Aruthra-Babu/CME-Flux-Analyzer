
import streamlit as st
import cdflib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CME Explorer – Aditya-L1", layout="wide")
st.title("☀️ CME Analysis – Aditya-L1 SWIS-ASPEX Explorer")

# Load the CDF file
cdf = cdflib.CDF("AL1_ASW91_L2_TH2_20250527_UNP_9999_999999_V02.cdf")

# Extract variables
time_raw = cdf.varget("epoch_for_cdf_mod")
flux = cdf.varget("integrated_flux_mod")
uncertainty = cdf.varget("flux_uncer")
energy = cdf.varget("energy_center_mod")

# Convert time to datetime
time = cdflib.cdfepoch.to_datetime(time_raw)

# Flatten if 2D (averaging across energy channels)
if len(flux.shape) > 1:
    flux = np.mean(flux, axis=1)
if len(uncertainty.shape) > 1:
    uncertainty = np.mean(uncertainty, axis=1)

# Build DataFrame
df = pd.DataFrame({
    "Time": time,
    "Flux": flux,
    "Uncertainty": uncertainty
})

# Sidebar: Filter
st.sidebar.header("📆 Filter by Date")
start_date = pd.to_datetime(st.sidebar.date_input("Start Date", df["Time"].min().date()))
end_date = pd.to_datetime(st.sidebar.date_input("End Date", df["Time"].max().date()))
filtered_df = df[(df["Time"] >= start_date) & (df["Time"] <= end_date)]

# Raw Data View
if st.checkbox("📄 Show Filtered Data Table"):
    st.write(filtered_df)

# Plot Flux
st.subheader("📈 Integrated Flux Over Time")
st.line_chart(filtered_df.set_index("Time")["Flux"])

# Anomaly Detection
st.subheader("⚠️ CME Flux Spike Detection")
threshold = st.slider("Set Flux Threshold", float(df["Flux"].min()), float(df["Flux"].max()), float(df["Flux"].mean()))
anomalies = filtered_df[filtered_df["Flux"] > threshold]
st.write("🔍 Possible CME Spikes Detected:")
st.dataframe(anomalies)

# Optional Plots
if st.checkbox("📉 Show Uncertainty Over Time"):
    st.line_chart(filtered_df.set_index("Time")["Uncertainty"])

if st.checkbox("🔬 Show Energy Channel Centers (eV)"):
    st.write("Energy Channels:")
    st.write(energy)
