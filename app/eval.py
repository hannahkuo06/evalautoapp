import concurrent
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


# client = AzureOpenAI(
#     azure_endpoint="https://openai-spm.openai.azure.com/",
#     api_key="d474a9b11bcb4417b5cb830f5ba8acac",
#     api_version="2024-02-15-preview"
# )


def get_negs(file, metrics):
    df = pd.read_csv(file, index_col=None)
    negs = df
    for metric in metrics:
        negs = negs[negs[metric] == 0]
    return negs


@functools.lru_cache(maxsize=None)
def predict_openai(prompt, temperature=0, max_tokens=50, top_k=1):
    message_text = [{"role": "system", "content": prompt}]
    response = client.chat.completions.create(
        model="gpt4",  # model = "deployment_name"
        messages=message_text,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    response_message = response.choices[0].message.content
    return response_message


async def parse_taxonomy(q_type, check, generated_text, expected_text):
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
            check_response = predict_openai(prompt)
            if 'Yes' in check_response:
                err_lst.append(err_name)
                explanations.append(check_response)

    if not err_lst:
        return ['GOOD'], explanations
    return err_lst, explanations


def analyze_metrics(record, metrics_list):
    with open('metrics.json', 'r') as f:
        metrics = json.load(f)

    incorrect_eval = []
    expl = []

    if record['generated_text'] != record['expected_text']:
        prompt = ("Is the generated text part of expected text?"
                  f"generated text: {record['generated_text']}"
                  f"expected text: {record['expected_text']}")
        check = predict_openai(prompt)
        # print(check)

        if check.__contains__('Yes'):
            incorrect_eval.append('METRIC ERROR')
            expl.append('Generated text contained in expected text')

    for met_type, lst in metrics.items():
        # print(met_type, lst)
        for m in metrics_list:
            if m in lst:
                # print(record[m])
                prompt = ("Analyze the model's metric assessment of this output:"
                          f"metric: {m}"
                          f"description: {lst[m]}"
                          f"generated text: {record['generated_text']}"
                          f"expected text: {record['expected_text']}"
                          f"model's assessment: {record[m]}")

                check = predict_openai(prompt)
                # print(check)

                if check.__contains__('incorrect'):
                    incorrect_eval.append(m)
                    expl.append(check)

    if not incorrect_eval:
        return ['GOOD'], expl

    return incorrect_eval, expl

async def get_type(question):
    type_q = f"What type of question is this? What type of answer is this question expecting? {question}"
    type_a = predict_openai(type_q)
    return type_a


async def check_type(gen_text, q_type):
    check_q = f"Is {gen_text} of the same type answer as stated in: {q_type}? State why."
    check_a = predict_openai(check_q)
    return check_a


async def converse(record):
    lst = ['exact_match', 'prefix_exact_match', 'quasi_exact_match', 'quasi_prefix_exact_match', 'contains_match']
    q_type = await get_type(record['inputs_pretokenized'])
    check = await check_type(record['generated_text'], q_type)
    errs, err_expl = await parse_taxonomy(q_type, check, record['generated_text'], record['expected_text'])
    met_evals, met_expl = analyze_metrics(record, lst)
    return errs, err_expl, met_evals, met_expl


async def process_batch(batch):
    tasks = [converse(row) for row in batch]
    results = await asyncio.gather(*tasks)
    return results


async def parallel(file_bytes, batch_size=50):
    df = pd.read_csv(BytesIO(file_bytes), index_col=None)
    batches = [df.iloc[i:i + batch_size] for i in range(0, len(df), batch_size)]

    errs = []
    expl = []
    mets = []
    met_expl = []

    for batch in batches:
        results = await process_batch(batch.to_dict(orient='records'))

        for result in results:
            errs.append(result[0])
            expl.append(result[1])
            print(type(results[2]))
            mets.append(result[2])
            met_expl.append(result[3])

    print(errs)
    print(mets)
    df['Error Analysis'] = errs
    df['Error Analysis Justification'] = expl
    df['Metric Analysis'] = mets
    df['Metric Analysis Justification'] = met_expl

    return df
