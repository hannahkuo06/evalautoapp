import asyncio
from io import BytesIO

import pandas as pd
import streamlit as st
import base64
import time
from app.parallelize import run_parallelize
from app.eval import get_negs

st.markdown("#### Instructions")
st.markdown("""
    1. Upload dataset CSV 
    2. Click 'Process
    3. View/Download the processed CSV
            """)


# @st.cache_data
def process(file, negatives=False):
    start_time = time.perf_counter()

    content_bytes = file.read()
    df = pd.read_csv(BytesIO(content_bytes), index_col=None)

    if negatives:
        metrics = ['exact_match', 'quasi_exact_match', 'prefix_exact_match', 'quasi_prefix_exact_match',
                   'contains_match']
        df = get_negs(df, metrics)
        df.reset_index()

    result_df = asyncio.run(run_parallelize(df))

    end_time = time.perf_counter()
    st.write(f"Computation runtime: {end_time - start_time:.6f} seconds")

    return result_df


def download_df(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Base 64 encode
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV file</a>'
    return href


uploaded_file = st.file_uploader("Choose a file", type=["csv", "json"], accept_multiple_files=False)

# name = st.text_input("metric name")
# description = st.text_input("metric description")
# if st.button("Add Metric"):
#     df = pd.DataFrame({name: description})

if st.button("Process Entire File") and uploaded_file is not None:
    with st.spinner("Processing your file..."):
        df = process(uploaded_file)
    st.markdown("---")
    st.write("✅ Evaluation complete!")
    st.write("Hover over the below table, and the download icon will appear in the top right corner of the table.")
    st.dataframe(df)

if st.button("Process Negatives Only") and uploaded_file is not None:
    with st.spinner("Processing your file..."):
        df = process(uploaded_file, True)
    st.markdown("---")
    st.write("✅ Evaluation complete!")
    st.write("Hover over the below table, and the download icon will appear in the top right corner of the table.")
    st.dataframe(df)
