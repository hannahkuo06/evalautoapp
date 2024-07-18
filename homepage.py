import streamlit as st

# st.markdown("### About")
st.markdown("This tool is meant to automate the error-checking process in data evaluation. "
            "It will process a runspec CSV and output the same CSV file with an extra column "
            "\"Errors\" that includes a list of errors/bugs GPT4 found in the generated text."
            "\n\n"
            "There is an editable JSON file that creates a hierarchy of errors that are commonly"
            "found during data evaluation. This way, we can manually include new errors for GPT4"
            "to keep an eye out for in the data for more accurate/detailed error-checking.")

# description of algorithm
# description of runspecs

st.markdown('#### Goal')
st.markdown('#### Processing')
# include example df here

st.markdown('#### Error Tags')
