import streamlit as st

st.set_page_config(page_title="Evaluation Automation",
                   page_icon=":chart_with_upwards_trend:",
                   layout="wide",
                   initial_sidebar_state="expanded")

st.title('EvalAutoApp')
st.subheader('Automated Runspec Error-Checking in Data Evaluation')


def navigate_to(page_name):
    st.session_state.page = page_name


def open_page(page_name):
    with open(page_name) as f:
        code = f.read()
        exec(code)


if 'page' not in st.session_state:
    st.session_state.page = 'Documentation'

st.sidebar.title('Navigation')
if st.sidebar.button('Documentation'):
    navigate_to('Documentation')

if st.sidebar.button('Processor'):
    navigate_to('Processor')

if st.session_state.page == 'Documentation':
    open_page('documentation.py')
if st.session_state.page == 'Processor':
    open_page('processor.py')
