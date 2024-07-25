import asyncio

import streamlit as st
import base64
import time
from app.eval import parallel_async


st.markdown("#### Instructions")
st.markdown("1. Upload dataset CSV \n2. Click 'Process'\n3. View/Download the processed csv")


# @st.cache_data
def process(file):
    start_time = time.perf_counter()
    content_bytes = file.read()
    # asyncio.run(asyncio.get_event_loop().set_debug(True))
    result_df = asyncio.run(parallel_async(content_bytes))

    end_time = time.perf_counter()
    st.write(f"Computation runtime: {end_time - start_time:.6f} seconds")

    # loop = asyncio.get_event_loop()
    # return loop.run_until_complete(parallel_async(content_bytes))

    return result_df


def download_df(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Base 64 encode
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV file</a>'
    return href


uploaded_file = st.file_uploader("Choose a file", type=["csv"], accept_multiple_files=False)

if st.button("Process") and uploaded_file is not None:
    df = process(uploaded_file)
    st.markdown("---")
    st.write("✅ Evaluation complete!")
    st.write("Hover over the below table, and the download icon will appear in the top right corner of the table.")
    st.data_editor(df)

    # st.markdown(download_df(df, 'output'), unsafe_allow_html=True)