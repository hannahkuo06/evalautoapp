import streamlit as st
import base64
import eval


st.markdown("### Instructions")
# note to download a csv
st.markdown("1. Upload csv of data \n2. Click 'Process'\n3. View/Download the processed csv")


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
    uploaded_file = st.file_uploader("Choose a file", type=["csv"], accept_multiple_files=False)

    if st.button("Process"):
        df = process(uploaded_file)
        st.markdown("---")
        st.write("Evaluation complete!")
        st.dataframe(df)

        # st.sidebar.title('Filter options')
        # st.sidebar.header('Metrics')
        #
        # st.sidebar.header('Errors')
        # search_term = st.text_input('Search for', '')

        # if search_term:
        #     filtered_df = df[df['Errors'].str.contains(search_term, case=False, na=False)]
        #     st.dataframe(filtered_df)
        #
        # else:
        #     filtered_df = df
        #     st.dataframe(filtered_df)


        st.markdown(download_df(df, 'output'), unsafe_allow_html=True)


if __name__ == '__main__':
    main()
