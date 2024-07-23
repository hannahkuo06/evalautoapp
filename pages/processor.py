import streamlit as st
import base64
from app.eval import para_process


st.markdown("#### Instructions")
st.markdown("1. Upload dataset CSV \n2. Click 'Process'\n3. View/Download the processed csv")


@st.cache_data
def process(file):
    content_bytes = file.read()
    return para_process(content_bytes)


def download_df(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Base 64 encode
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV file</a>'
    return href


uploaded_file = st.file_uploader("Choose a file", type=["csv"], accept_multiple_files=False)

if st.button("Process") and uploaded_file is not None:
    df = process(uploaded_file)
    st.markdown("---")
    st.write("Evaluation complete!")
    # print(type(df))
    st.write(df)

    st.markdown(download_df(df, 'output'), unsafe_allow_html=True)