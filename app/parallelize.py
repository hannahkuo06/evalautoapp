import asyncio
from concurrent.futures import ThreadPoolExecutor

from .eval import converse, get_negs, analyze_metrics


# Define the async function to process a batch of records
async def process_batch(batch):
    results = []
    metrics = ['exact_match', 'quasi_exact_match', 'prefix_exact_match', 'quasi_prefix_exact_match', 'contains_match']

    for _, record in batch.iterrows():
        analyze_result, converse_result = await asyncio.gather(
            analyze_metrics(record, metrics),
            converse(record)
        )

        results.append((analyze_result, converse_result))
        # results.append(converse_result)

    return results


# Define the async function to execute the processing
async def execute(df, batch_size=10):
    errs = []
    errs_expl = []
    mets = []
    mets_expl = []

    with ThreadPoolExecutor() as executor:
        batches = [df.iloc[i:i + batch_size] for i in range(0, len(df), batch_size)]
        tasks = [process_batch(batch, executor) for batch in batches]

        # Await all tasks and gather results
        results = await asyncio.gather(*tasks)

        # Process results
        for batch_results in results:
            for result in batch_results:
                metrics, errors = result
                errs.append(errors[0])
                errs_expl.append(errors[1])
                mets.append(metrics[0])
                mets_expl.append(metrics[1])

    df['Error Analysis'] = errs
    df['Error Analysis Justification'] = errs_expl
    df['Metric Analysis'] = mets
    df['Metric Analysis Justification'] = mets_expl

    return df


# Define the main async function to run the processing
async def run_parallelize(df):
    return await execute(df)
