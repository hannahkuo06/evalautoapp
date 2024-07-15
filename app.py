import base64
import streamlit as st
import eval


@st.cache_data
def process(file):
    content_bytes = file.read()
    return eval.parallelize(content_bytes)


def download_df(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Base 64 encode
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV file</a>'
    return href


def main():
    st.set_page_config(page_title="Evaluation Automation", page_icon=":chart_with_upwards_trend:")
    st.header("Linguistic Error-checking Automation")

    st.markdown("### About")
    st.markdown("This tool is meant to automate the error-checking process in data evaluation. "
                "It will process a runspec CSV and output the same CSV file with an extra column "
                "\"Errors\" that includes a list of errors/bugs GPT4 found in the generated text.")

    st.markdown("### Instructions")
    st.markdown("1. Upload csv of data \n2. Click 'Process'\n3. View/Download the processed csv")

    uploaded_file = st.file_uploader("Choose a file", type=["csv"], accept_multiple_files=False)

    if st.button("Process"):
        processed_data = process(uploaded_file)
        st.markdown("---")
        st.write("Evaluation complete!")
        st.write(processed_data)

        st.markdown(download_df(processed_data, 'output'), unsafe_allow_html=True)


if __name__ == '__main__':
    main()