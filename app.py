import base64
import streamlit as st
import eval

st.set_page_config(page_title="Evaluation Automation",
                   page_icon=":chart_with_upwards_trend:",
                   layout="wide",
                   initial_sidebar_state="expanded")

# st.sidebar.title("Navigation")
# pages = {
#     "Documentation": "homepage.py",
#     "Upload File and Process": "processor.py",
# }

# st.markdown(
#     """
#     <div class="navbar">
#         <button onclick="location.href='#home'">Home</button>
#         <button onclick="location.href='#upload'">Upload File</button>
#         <button onclick="location.href='#page3'">Page 3</button>
#     </div>
#     """,
#     unsafe_allow_html=True
# )

# Create layout for the main content
home_col, upload_col = st.columns([1, 1])

with home_col:
    if st.button("Home"):
        import homepage

with upload_col:
    if st.button("Upload File"):
        import processor

# Default to Home
import homepage


st.header("Linguistic Error-checking Automation")

# selection = st.sidebar.radio("Go to", list(pages.keys()))
#
# page = pages[selection]
#
#
# with open(page) as f:
#     code = f.read()
#     exec(code)

# @st.cache_data
# def process(file):
#     content_bytes = file.read()
#     return eval.parallelize(content_bytes)
#
#
# def download_df(df, filename):
#     csv = df.to_csv(index=False)
#     b64 = base64.b64encode(csv.encode()).decode()  # Base 64 encode
#     href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV file</a>'
#     return href
#
#
# def main():
#     st.set_page_config(page_title="Evaluation Automation",
#                        page_icon=":chart_with_upwards_trend:",
#                        layout="wide")
#     st.header("Linguistic Error-checking Automation")
#
#     st.markdown("### About")
#     st.markdown("This tool is meant to automate the error-checking process in data evaluation. "
#                 "It will process a runspec CSV and output the same CSV file with an extra column "
#                 "\"Errors\" that includes a list of errors/bugs GPT4 found in the generated text."
#                 "\n\n"
#                 "There is an editable JSON file that creates a hierarchy of errors that are commonly"
#                 "found during data evaluation. This way, we can manually include new errors for GPT4"
#                 "to keep an eye out for in the data for more accurate/detailed error-checking.")
#
#     st.markdown("### Instructions")
#     st.markdown("1. Upload csv of data \n2. Click 'Process'\n3. View/Download the processed csv")
#
#     uploaded_file = st.file_uploader("Choose a file", type=["csv"], accept_multiple_files=False)
#
#     if st.button("Process"):
#         df = process(uploaded_file)
#         st.markdown("---")
#         st.write("Evaluation complete!")
#         st.dataframe(df)
#
#         # st.sidebar.title('Filter options')
#         # st.sidebar.header('Metrics')
#         #
#         # st.sidebar.header('Errors')
#         # search_term = st.text_input('Search for', '')
#
#         # if search_term:
#         #     filtered_df = df[df['Errors'].str.contains(search_term, case=False, na=False)]
#         #     st.dataframe(filtered_df)
#         #
#         # else:
#         #     filtered_df = df
#         #     st.dataframe(filtered_df)
#
#
#         st.markdown(download_df(df, 'output'), unsafe_allow_html=True)
#
#
# if __name__ == '__main__':
#     main()
