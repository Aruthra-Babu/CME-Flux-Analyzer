import streamlit as st
import cdflib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tempfile

st.set_page_config(page_title="CME Flux Analyzer – Aditya-L1", layout="wide")
st.title("☀️ CME Flux Analyzer – Aditya-L1 SWIS-ASPEX")

# Upload file
uploaded_file = st.file_uploader("📂 Upload your Aditya-L1 .cdf file", type="cdf")

if uploaded_file is not None:
    # Save uploaded BytesIO to a temporary file for cdflib to read
    with tempfile.NamedTemporaryFile(delete=False, suffix=".cdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    cdf = cdflib.CDF(tmp_path)

    # Extract key variables
    time_raw = cdf.varget("epoch_for_cdf_mod")
    flux = cdf.varget("integrated_flux_mod")
    uncertainty = cdf.varget("flux_uncer")
    energy = cdf.varget("energy_center_mod")

    # Convert epoch to datetime
    time = cdflib.cdfepoch.to_datetime(time_raw)

    # Handle multidimensional arrays
    if len(flux.shape) > 1:
        flux = np.mean(flux, axis=1)
    if len(uncertainty.shape) > 1:
        uncertainty = np.mean(uncertainty, axis=1)

    # Create DataFrame
    df = pd.DataFrame({
        "Time": time,
        "Flux": flux,
        "Uncertainty": uncertainty
    })

    # Time difference between samples
    df["Time_Diff(s)"] = df["Time"].diff().dt.total_seconds().fillna(0)

    # Sidebar filtering
    st.sidebar.header("📆 Date Filter")
    start_date = pd.to_datetime(st.sidebar.date_input("Start Date", df["Time"].min().date()))
    end_date = pd.to_datetime(st.sidebar.date_input("End Date", df["Time"].max().date()))
    filtered_df = df[(df["Time"] >= start_date) & (df["Time"] <= end_date)]

    # Threshold slider
    st.sidebar.header("⚠️ CME Spike Detection")
    threshold = st.sidebar.slider("Set Flux Threshold", float(df["Flux"].min()), float(df["Flux"].max()), float(df["Flux"].mean()))

    # Detect spikes
    spike_df = filtered_df[filtered_df["Flux"] > threshold]

    # Warning message if spikes found
    if not spike_df.empty:
        st.warning(f"🚨 Alert: {len(spike_df)} CME flux spike(s) detected above threshold {threshold:.2f}!")

    # 📈 Flux Plot with Spikes
    st.subheader("📈 Integrated Flux Over Time with Spikes")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(filtered_df["Time"], filtered_df["Flux"], label="Flux", color="blue")
    ax.scatter(spike_df["Time"], spike_df["Flux"], color="red", label="Spikes")
    ax.set_xlabel("Time")
    ax.set_ylabel("Flux")
    ax.set_title("Flux vs Time (Spikes Highlighted in Red)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # 📊 Data Table
    if st.checkbox("📄 Show Filtered Data Table"):
        st.write(filtered_df)

    # 🚨 Spike Table
    st.subheader("🚨 Detected CME Spike Events")
    st.dataframe(spike_df)

    # 📥 Download Spike Data
    st.download_button(
        label="📥 Download Spike Data as CSV",
        data=spike_df.to_csv(index=False).encode('utf-8'),
        file_name='cme_spike_report.csv',
        mime='text/csv'
    )

    # 📉 Uncertainty Plot
    if st.checkbox("📉 Show Flux Uncertainty Over Time"):
        fig2, ax2 = plt.subplots(figsize=(12, 4))
        ax2.plot(filtered_df["Time"], filtered_df["Uncertainty"], color="purple")
        ax2.set_title("Uncertainty over Time")
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Uncertainty")
        ax2.grid(True)
        st.pyplot(fig2)

    # 🔬 Energy Channels
    if st.checkbox("🔬 Show Energy Channel Centers (eV)"):
        st.write("Energy Channels:", energy)

else:
    st.info("Please upload a `.cdf` file to begin analysis.")
