import functools
import pandas as pd
import json
import yaml
# import multiprocessing

from openai import AzureOpenAI
from io import BytesIO


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
def predict_openai(prompt, temperature=0.3, max_tokens=1500, top_k=50):
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
def response_type_check(record):
    prompt = ("Context: The given file gives you an inputted prompt, the generated text, and the expected text."
              "Your job is to analyze this using the columns given in the file."
              ""
              "Prompt: What kind of test question is the prompt? Taking into account the context of the question,"
              "what type of answer is this question looking for?"
              " Do not give the answer to the question itself. Be concise."
              f"Data:{record}")

    return predict_openai(prompt)


# using analysis from response_type_check, checks if generated answer is correct
def error_check(record, type_check):
    prompt = ("Based on the analysis given:"
              "1. Does the generated answer give the same answer type as stated in the analysis? List why."
              "2. Does the generated answer match the expected answer exactly? If not, what is the issue?"
              ""
              "Always start answer for each part with 'Yes' or 'No'. \n"
              ""
              f"Question: {record['inputs_pretokenized']}\n"
              f"Analysis: {type_check}\n"
              f"Generated Answer (generated by the model): {record['generated_text']} \n"
              f"Expected Answer (expected answer): {record['expected_text']}\n")

    response = predict_openai(prompt)

    if "1. Yes" in response and "2. Yes" in response:
        return "Good"
    else:
        errors = parse_taxonomy(response, record['generated_text'], record['expected_text'])
        if errors is []:
            return "Other"
        else:
            return errors


def parse_taxonomy(input, generated_text, expected_text):
    with open('errors.json', 'r') as f:
        taxonomy = json.load(f)

    err_lst = []

    for err_type, type_info in taxonomy['Errors'].items():
        for err_name, err_info in type_info['errors'].items():
            prompt = (f"Below is the found error and some information."
                      f""
                      f"Generated text: {generated_text}\n"
                      f"Expected text: {expected_text}\n"
                      f"Error: {input}\n"
                      f"Prompt: {err_info['_description']}"
                      f"Examples: {err_info['_examples']}\n"
                      f""
                      f"Respond yes or no")
            check = predict_openai(prompt)
            if check == 'Yes':
                err_lst.append(err_name)

    return err_lst


@functools.lru_cache(maxsize=None)
def analyze(file_bytes):
    df = pd.read_csv(BytesIO(file_bytes), index_col=None)
    df['Errors'] = None

    for _, row in df.iterrows():
        resp_type = response_type_check(row)
        ec = error_check(row, resp_type)
        df.loc[df['id'] == row['id'], 'Errors'] = str(ec)
    return df
