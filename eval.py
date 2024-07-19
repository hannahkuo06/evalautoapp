import functools
import pandas as pd
import json
import yaml
from multiprocessing import Pool

from openai import AzureOpenAI
from io import BytesIO, StringIO

# def load_config():
#     with open('config.yaml', 'r') as file:
#         return yaml.safe_load(file)


# config = load_config()
# api_key = config.get('api_key')

client = AzureOpenAI(
    azure_endpoint="https://core-llm-1.openai.azure.com/",
    api_key="1456d60bb6864ed99bd5cc4858ed75a8",
    api_version="2024-02-15-preview",
)


# returns df of negatives from file.
# Takes in a list of metrics in the case more than one metric is used to evaluate
def get_negs(file, metrics):
    df = pd.read_csv(file, index_col=None)
    negs = df
    for metric in metrics:
        negs = negs[negs[metric] == 0]
    return negs


@functools.lru_cache(maxsize=None)
def predict_openai(prompt, temperature=0.3, max_tokens=100, top_k=50):
    message_text = [{"role": "system", "content": prompt}]
    response = client.chat.completions.create(
        model="GPT4",  # model = "deployment_name"
        messages=message_text,
        temperature=temperature,
        max_tokens=max_tokens
        # parallel_tool_calls=True
    )

    response_message = response.choices[0].message.content
    return response_message


# checks the required answer type for prompt
# def response_type(record):
#     prompt = ("Context: The given file gives you an inputted prompt."
#               "Your job is to analyze this using the columns given in the file."
#               ""
#               "Prompt: What kind of test question is the prompt? Taking into account the context of the final question,"
#               "what type of answer is this type of question looking for?"
#               " Do not give the answer to the question itself. Be concise."
#               f"Data:{[record['inputs_pretokenized']]}")
#
#     return predict_openai(prompt)


# using analysis from response_type_check, checks if generated answer is correct
# def error_check(record, type_check):
#     prompt = ("Based on the analysis given:"
#               "1. Does the generated answer type match the analysis? List why."
#               "2. Does the generated answer match the expected answer exactly? If not, what is the issue?"
#               ""
#               "Always start answer for each part with 'Yes' or 'No'. \n"
#               ""
#               f"Question: {[record['inputs_pretokenized']]}\n"
#               f"Analysis: {type_check}\n"
#               f"Generated Answer (generated by the model): {record['generated_text']} \n"
#               f"Expected Answer (expected answer): {record['expected_text']}\n")
#
#     response = predict_openai(prompt)
#
#     if "1. Yes" in response and "2. Yes" in response:
#         return "Good", response
#     else:
#         errors = parse_taxonomy(response, record['generated_text'], record['expected_text'])
#         if errors is []:
#             return "Other", response
#         else:
#             return errors, response

    # return response


def parse_taxonomy(input, generated_text, expected_text):
    # print("Gen:", generated_text, "Exp:", expected_text)
    with open('errors.json', 'r') as f:
        taxonomy = json.load(f)

    err_lst = []
    explanations = []

    for err_type, type_info in taxonomy['Errors'].items():
        for err_name, err_info in type_info['errors'].items():
            prompt = (f"Below is the found error and some information."
                      f""
                      f"Generated text: {generated_text}\n"
                      f"Expected text: {expected_text}\n"
                      f"Error: {input}\n"
                      f"Prompt: {err_info['_description']}, state why."
                      f"Examples: {err_info['_examples']}\n"
                      f"")
                      # f"Respond yes or no")
            check = predict_openai(prompt)
            if check.__contains__('Yes'):
                err_lst.append(err_name)
                explanations.append(check)

    if not err_lst:
        return 'Good'
    return err_lst, explanations

    # return check

# @functools.lru_cache(maxsize=None)
# def process_row(row):
#     resp_type = response_type(row)
#     tag, justification = error_check(row, resp_type)
#     # print(tag, justification)
#     return tag, justification
#
#
# def process_batch(batch):
#     tags = []
#     justifications = []
#     for _, row in batch.iterrows():
#         tag, justification = process_row(row)
#         # print(tag)
#         tags.append(tag)
#         justifications.append(justification)
#     # print(tags)
#     return tags, justifications


def add_col(df, col_name, values):
    # print(values)
    df[col_name] = values
    return df


# def parallelize(file_bytes, num_processes=4):
#     file_string = file_bytes.decode('utf-8')
#     data = StringIO(file_string)
#     df = pd.read_csv(data)
#     # df = pd.read_csv(BytesIO(file_bytes), index_col=None)
#     chunk_size = len(df) // num_processes
#     chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
#
#     with Pool(num_processes) as pool:
    #     results = pool.map(process_batch, chunks)
    #     # print(results)
    #
    #     tags = []
    #     justifications = []
    #
    #     for tag, justification in results:
    #         # print(tag)
    #         for t in tag:
    #             tags.append(t)
    #
    #         for j in justification:
    #             justifications.append(j)
    #
    # # results = [item for sublist in tags for item in sublist]
    #
    # df = add_col(df, 'Errors', tags)
    # df = add_col(df, 'Justifications', justifications)
    # # df['Errors'] = tags
    # # # print(justification)
    # # df['Justifications'] = justifications
    # return df

# def batch(chunk):
#     tags = []
#     justifications = []
#     for _, row in batch.iterrows():
#         justification = process_row(row)
#         # print(tag)
#         # tags.append(tag)
#         justifications.append(justification)
#     # print(tags)
#     return justifications

def parallelize2(file_bytes, num_processes=4):
    df = pd.read_csv(BytesIO(file_bytes), index_col=None)
    # print(df)
    chunk_size = len(df) // num_processes
    chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

    with Pool(num_processes) as pool:
        results = pool.map(converse, chunks)
        # print(results)

        tags = []
        justifications = []

        for tag, justification in results:
            # print(tag)
            # print(justification)
            # for t in tag:
            #     tags.append(t)
            #
            # for j in justification:
            #     justifications.append(j)

            tags.append(tag)
            justifications.append(justification)

    # results = [item for sublist in tags for item in sublist]
    # print(len(tags))

    df = add_col(df, 'Errors', tags)
    df = add_col(df, 'Justifications', justifications)
    return df

def converse(record):
    # with open('errors.json', 'r') as f:
    #     taxonomy = json.load(f)
    # print(record)
    # print("gen:", record['generated_text'])
    # print("exp:", record['expected_text'])

    type_q = f"What kind of question is this? What type of answer is it looking for? {[record['inputs_pretokenized']]}"
    type_a = predict_openai(type_q)
    # print(type_a)

    check_q = f"Is {record['generated_text']} of the same type as stated in: {type_a}? State why. "
    check_a = predict_openai(check_q)
    # print(check_a)

    # answer_q = (f"Given the information previously given, is there anything wrong with the outputs? Begin with yes or no, state why."
    #             f"Generated:{record['generated_text']}, Expected: {record['expected_text']}, "
    #             f"Context: {[record['inputs_pretokenized']]}"
    #             f"Other information: {type_a}, {check_a}")
    # answer_a = predict_openai(answer_q)

    errs, expl = parse_taxonomy(type_a + check_a, record['generated_text'], record['expected_text'])

    # for err_type, type_info in taxonomy['Errors'].items():
    #     for err_name, err_info in type_info['errors'].items():
    #         errors_q = (f"Prompt: {err_info['_description']},"
    #                     f"Context: {[record['inputs_pretokenized']]},"
    #                     f"Generated text: {record['generated_text']}"
    #                   f"Expected text: {record['expected_text']},"
    #                   f"Error: {err_name}\n")
    #         errors_a = predict_openai(errors_q)

    # return errs, check_a + answer_a
    return errs, expl


# @functools.lru_cache(maxsize=None)
# def analyze(file_bytes):
#     df = pd.read_csv(BytesIO(file_bytes), index_col=None)
#     df['Errors'] = None
#
#     # with Pool(3) as pool:
#     #     result = pool.map()
#
#     for _, row in df.iterrows():
#         resp_type = response_type_check(row)
#         ec = error_check(row, resp_type)
#         df.loc[df['id'] == row['id'], 'Errors'] = str(ec)
#     return df
