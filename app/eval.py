import functools
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import json
import asyncio
import aiohttp
from io import BytesIO
from openai import AzureOpenAI

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
def predict_openai(session, prompt, temperature=0, max_tokens=50, top_k=1):
    message_text = [{"role": "system", "content": prompt}]
    response = client.chat.completions.create(
        model="GPT4",  # model = "deployment_name"
        messages=message_text,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    response_message = response.choices[0].message.content
    return response_message

    # url = ENDPOINT
    # headers = {
    #     'Authorization': client.api_key,
    #     'Content-Type': 'application/json'
    # }
    # payload = {
    #     'model': 'GPT4',
    #     'prompt': prompt,
    #     'max_tokens': max_tokens
    # }
    #
    # async with session.post(url, headers=headers, json=payload) as response:
    #     if response.status == 200:
    #         result = response.json()
    #         return result['choices'][0]['text']
    #     else:
    #         return f"Error: {response.status} - {await response.text()}"


async def parse_taxonomy(session, q_type, check, generated_text, expected_text):
    errs = q_type, check
    with open('errors.json', 'r') as f:
        taxonomy = json.load(f)

    err_lst = []
    explanations = []

    for err_type, type_info in taxonomy['Errors'].items():
        for err_name, err_info in type_info['errors'].items():
            prompt = (
                f"Below is the found error and some information.\n"
                f"Generated text: {generated_text}\n"
                f"Expected text: {expected_text}\n"
                f"Previous analysis: {errs}\n"
                f"Prompt: {err_info['_description']}, state why in max 2 sentences.\n"
                f"Examples: {err_info['_examples']}\n"
            )
            check_response = predict_openai(session, prompt)
            if 'Yes' in check_response:
                err_lst.append(err_name)
                explanations.append(check_response)

    if not err_lst:
        return 'GOOD', explanations
    return err_lst, explanations


async def get_type(session, question):
    type_q = f"What type of question is this? What type of answer is this question expecting? {question}"
    type_a = predict_openai(session, type_q)
    return type_a


async def check_type(session, gen_text, q_type):
    check_q = f"Is {gen_text} of the same type answer as stated in: {q_type}? State why."
    check_a = predict_openai(session, check_q)
    return check_a


async def converse(record, session):
    q_type = await get_type(session, record['inputs_pretokenized'])
    check = await check_type(session, record['generated_text'], q_type)
    err_tuple = await parse_taxonomy(session, q_type, check, record['generated_text'], record['expected_text'])
    tags, expl = err_tuple
    return tags, expl


async def parallel_async(file_bytes, batch_size=10):
    df = pd.read_csv(BytesIO(file_bytes), index_col=None)

    # results_list = []
    results = []

    async with aiohttp.ClientSession() as session:
        loop = asyncio.get_event_loop()
        # with ThreadPoolExecutor(max_workers=4) as executor:
        #     # tasks = [converse(row, session) for _, row in df.iterrows()]
        #     tasks = [loop.run_in_executor(executor, converse, row, session) for _, row in df.iterrows()]
        #     results = await asyncio.gather(*tasks)
        with ThreadPoolExecutor(max_workers=4) as executor:
            tasks = []
            for _, row in df.iterrows():
                tasks = []
                for i in range(0, len(df), batch_size):
                    batch = df.iloc[i:i + batch_size]
                    batch_tasks = [loop.run_in_executor(executor, converse, row, session) for _, row in
                                   batch.iterrows()]
                    tasks.extend(batch_tasks)


    tags_list, expl_list = zip(*results)
    # print(tags_list)
    # print(expl_list)

    # Assign results to DataFrame
    df['Errors'] = tags_list
    df['Justification'] = expl_list

    return df


    # for result in results:
    #     results_list.extend(result)

    # print(results_list)
    # return results

    # Uncomment and modify these lines if you want to include results in the dataframe
    # result1, result2 = zip(*results)
    # df['Errors'] = result1
    # df['Justification'] = result2
    # return df