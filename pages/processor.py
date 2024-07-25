import asyncio

import streamlit as st
import base64
import time
from app.eval import parallel


st.markdown("#### Instructions")
st.markdown("1. Upload dataset CSV \n2. Click 'Process'\n3. View/Download the processed csv")


@st.cache_data
def process(file):
    start_time = time.perf_counter()

    content_bytes = file.read()
    result_df = asyncio.run(parallel(content_bytes))

    end_time = time.perf_counter()
    st.write(f"Computation runtime: {end_time - start_time:.6f} seconds")

    return result_df


def download_df(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Base 64 encode
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV file</a>'
    return href


uploaded_file = st.file_uploader("Choose a file", type=["csv"], accept_multiple_files=False)

if st.button("Process") and uploaded_file is not None:
    with st.spinner("Processing your file..."):
        df = process(uploaded_file)
    st.markdown("---")
    st.write("✅ Evaluation complete!")
    st.write("Hover over the below table, and the download icon will appear in the top right corner of the table.")
    st.data_editor(df)
