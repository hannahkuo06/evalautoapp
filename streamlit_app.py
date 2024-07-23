import os
import sys

import streamlit as st

module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.insert(0, module_dir)

st.set_page_config(page_title="Evaluation Automation",
                   page_icon=":chart_with_upwards_trend:",
                   layout="wide",
                   initial_sidebar_state="expanded")
pg = st.navigation([
    st.Page("pages/documentation.py", title="Documentation", icon="📝", default=True),
    st.Page("pages/processor.py", title="Processor", icon="💻"),
])

st.title('EvalAutoApp')
st.subheader('Automated Runspec Error-Checking in Data Evaluation')

pg.run()