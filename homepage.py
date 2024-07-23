import json

import pandas as pd
import streamlit as st

sections = {
    "Goal": "goal",
    "The Algorithm": "the_algorithm",
    "Example Visual": "example_visual",
    "Error Tags": "error_tags",
    "Next Steps": "next_steps"
}

st.sidebar.title("Documentation")
selection = st.sidebar.radio("Go to", list(sections.keys()))

input_df = pd.read_csv('data/fake_data.csv')
output_df = pd.read_csv('data/example_fake_data_output.csv')

with open('errors.json', 'r') as file:
    errors = json.load(file)

if selection == "Goal":
    st.markdown("<a id='goal'></a>", unsafe_allow_html=True)
    st.markdown('#### Goal')
    st.markdown("""
        Currently, linguists are tasked with inspecting spreadsheets of model results, making notes of any errors found in 
        an additional 'Comments' column to be sent to the engineering team for further training or validation. 
        This process is manual and tedious, and linguists should be able to concentrate their niche skills elsewhere. 
                
        This tool aims to simplify and streamline the data evaluation process for linguists using GPT4. Specifically, it 
        automates linguistic error checking on Excel spreadsheets of the model results by adding columns with notes about
        the errors found, greatly reducing the time and effort required to assess and analyze the data. Linguists can then
        spotcheck, refine, and summarize the errors or directly send this table as a CSV to engineering.
        """)

elif selection == "The Algorithm":
    st.markdown("<a id='the_algorithm'></a>", unsafe_allow_html=True)
    st.markdown("#### The Algorithm")
    st.markdown("<u>The Components</u>", unsafe_allow_html=True)
    st.markdown("""
                - **Runspec**: includes the dataset with prompts as well as other information such as its postprocessor,
                    preprocessor, etc. The only field of a runspec relevant for this tool is the dataset.
                - **CSV of data**: a CSV of a runspec's dataset. It should include columns such as 'expected_text',
                    'generated_text', and 'inputs_pretokenized'. The data found on Toolkit would already be in this format 
                    if you download from there.
                - **Dynamic JSON error taxonomy**: There is an editable JSON file `errors.json` that creates a hierarchy of errors that 
                    are commonly found during data evaluation. This way, new errors can be manually added for GPT4 to keep
                    an eye out for in the data sheets for more accurate and detailed error-checking.
                    """)

    st.markdown("<u>The Process</u>", unsafe_allow_html=True)
    st.markdown("""
        1. **Answer Type**: 
            First, the input prompt is sent into GPT4, asking for the type of answer it is looking for (ex. multiple 
            choice, name, numerical answer...)
        2. **Type Check**:
            GPT4 compares the generated text with the output from the previous part to check if the generated output 
            type is correct. (ex. prompt is multiple choice, does the generated text return A, B, C, or D?)
        3. **Parse Taxonomy**:
            Taking the results from the previous parts, we ask GPT4 again to make an assessment using our `errors.json` 
            file. It will return both the tags it matches and a max 2 sentence reasoning for its labeling.
    """)

    st.markdown("<u>The Output</u>", unsafe_allow_html=True)
    st.markdown("""
                - **CSV file**: The same input data file with additional columns
                    - **Errors column**: A column containing a list of error tags as identified by GPT4 according to
                     `errors.json`.
                    - **Justifications column**: A column containing a list of short explanations for why the tags were
                    given by GPT4.
    """)
    st.markdown("""
        The dataset is obtained through the runspec. Most of the data should be accessible through Toolkit.
        
        EvalAutoApp first takes in an uploaded file and processes the prompt. Then it compares the expected text and
        generated text, assessing for errors, before outputting a CSV with the relevant information in the new columns.
                """)

elif selection == "Example Visual":
    st.markdown("<a id='example_visual'></a>", unsafe_allow_html=True)
    st.markdown('#### Example Visual')
    st.markdown("Here are some visual steps to follow regarding the processing of a runspec\'s dataset. Feel free to"
                "scroll through the tables to see more columns.")

    st.dataframe(input_df)
    st.markdown("This is the data provided in `fake_data.csv`, located in the `data` folder on GitHub. Note there is no "
                "'Errors' or 'Justifications' column'. Now we run it through the 'Upload File and Process' page...")
    # include example df here
    st.dataframe(output_df)
    st.markdown("The new columns are added with the relevant information populated.")

elif selection == "Error Tags":
    st.markdown("<a id='error_tags'></a>", unsafe_allow_html=True)
    st.markdown('#### Error Tags')
    st.markdown("The errors GPT4 will find will depend on how `errors.json` is defined and labeled. Here are default "
                "errors in the file:")
    st.json(errors)

elif selection == "Next Steps":
    st.markdown("<a id='next_steps'></a>", unsafe_allow_html=True)
    st.markdown("#### Next Steps")

    st.markdown("<u>Runtime</u>", unsafe_allow_html=True)
    st.markdown("""
            Most immediately, the runtime will need to be improved. Currently, there is some parallelization, but refining
            the code to be able to efficiently processes hundreds of rows in a dataset would be best.
    """)

    st.markdown("<u>Metrics</u>", unsafe_allow_html=True)
    st.markdown("""
            As of July 23, 2023, EvalAutoApp does not take existing metrics into account. As such, it functions as an 
            additional metric itself. A future step would be to incorporate the existing metric scores into this error 
            evaluation in order to better understand, assess, and analyze the data accurately.
    """)

    st.markdown("<u>Summarization</u>", unsafe_allow_html=True)
    st.markdown("""
            Each dataset file spans hundreds (sometimes thousands) of rows. Spotchecking that many error tags would 
            eventually become a tedious task in itself as well. Including a summarization feature that would list the 
            top three errors and list a couple relevant records would be extremely helpful and enhance this process for 
            linguists.
    """)

    st.markdown("<u>User-friendly Features</u>", unsafe_allow_html=True)
    st.markdown("""
            Adding more features with the target user audience in mind would make this tool more robust. Since it is
            most probable that the user does not have a technical background, adding more features such as an 
            interactive dataframe to accommodate and reduce the technicalities in using the tool would be ideal.
    """)