import functools
import pandas as pd
import json
import asyncio
import aiohttp

# from concurrent.futures import ProcessPoolExecutor

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

ENDPOINT = "https://core-llm-1.openai.azure.com/"

# returns df of negatives from file.
# Takes in a list of metrics in the case more than one metric is used to evaluate
def get_negs(file, metrics):
    df = pd.read_csv(file, index_col=None)
    negs = df
    for metric in metrics:
        negs = negs[negs[metric] == 0]
    return negs


@functools.lru_cache(maxsize=None)
async def predict_openai(session, prompt, temperature=0, max_tokens=50, top_k=1):
    message_text = [{"role": "system", "content": prompt}]
    response = client.chat.completions.create(
        model="GPT4",  # model = "deployment_name"
        messages=message_text,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    headers = {
        'Authorization': f'Bearer {client.api_key}',
        'Content-Type': 'application/json'
    }
    json_data = {
        'model': 'gpt-4',
        'messages': [{'role': 'system', 'content': prompt}],
        'temperature': 0.7
    }

    async with session.post(ENDPOINT, headers=headers, json=json_data) as response:
        response_data = await response.json()
        return response_data['choices'][0]['message']['content']

    # response_message = response.choices[0].message.content
    # return response_message


async def parse_taxonomy(session, errs, generated_text, expected_text):
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
                      f"Previous analysis: {errs}\n"
                      f"Prompt: {err_info['_description']}, state why in max 2 sentences."
                      f"Examples: {err_info['_examples']}\n"
                      f"")
            check = await predict_openai(session, prompt)
            if check.__contains__('Yes'):
                err_lst.append(err_name)
                explanations.append(check)

    if not err_lst:
        return 'GOOD', explanations
    return err_lst, explanations


async def get_type(session, question):
    type_q = f"What type of question is this? What type of answer is this question expecting? {[question]}"
    type_a = await predict_openai(session, type_q)
    return type_a


async def check_type(session,gen_text, q_type):
    check_q = f"Is {gen_text} of the same type answer as stated in: {q_type}? State why. "
    check_a = await predict_openai(session, check_q)
    return check_a


async def converse(record, session):
    q_type = await get_type(session, record['inputs_pretokenized'])
    check = await check_type(session, record['generated_text'], q_type)
    err_tuple = await parse_taxonomy(session, q_type + check, record['generated_text'], record['expected_text'])
    errs, expl = err_tuple
    return errs, expl

async def parallel_async(file_bytes):
    df = pd.read_csv(BytesIO(file_bytes), index_col=None)

    async with aiohttp.ClientSession() as session:
        tasks = [converse(row, session) for _, row in df.iterrows()]
        results = await asyncio.gather(*tasks)

    result1, result2 = zip(*results)

    df['Errors'] = result1
    df['Justification'] = result2

    return df
