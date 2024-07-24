import streamlit as st

st.set_page_config(page_title="Evaluation Automation",
                   page_icon="🗒",
                   layout="wide",
                   initial_sidebar_state="expanded")
pg = st.navigation([
    st.Page("pages/documentation.py", title="Documentation", icon="📄", default=True),
    st.Page("pages/processor.py", title="Processor", icon="⚙️"),
])

st.title('🗒 EvalAutoApp')
st.subheader('Automated Runspec Error-Checking in Data Evaluation')

pg.run()