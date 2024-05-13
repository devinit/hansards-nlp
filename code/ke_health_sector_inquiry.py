import os
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
import math
import click
import json
from glob import glob
from tqdm import tqdm


load_dotenv()
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

MODEL = "gpt-3.5-turbo-0125"


def chunk_by_tokens(tokenizer, input_text, model_max_size):
    chunks = list()
    tokens = tokenizer.encode(input_text)
    token_length = len(tokens)
    desired_number_of_chunks = math.ceil(token_length / model_max_size)
    calculated_chunk_size = math.ceil(token_length / desired_number_of_chunks)
    for i in range(0, token_length, calculated_chunk_size):
        chunks.append(tokenizer.decode(tokens[i:i + calculated_chunk_size]))
    return chunks


def warn_user_about_tokens(tokenizer, batches, other_prompts):
    token_cost = 0.50
    token_cost_per = 1000000
    token_count = 0
    for batch in batches:
        token_count += len(tokenizer.encode(batch))
        token_count += len(tokenizer.encode(other_prompts))
    return click.confirm(
        "This will use at least {} tokens and cost at least ${} to run. Do you want to continue?".format(
        token_count, round((token_count / token_cost_per) * token_cost, 2)
    )
    , default=False)


if __name__ == '__main__':
    system_prompt = (
        "You are a helpful assistant that uses the extract_attributes function "
        "to extract attributes of a transcript as JSON for a database. "
        "Always use the extract_attributes function. "
        "All of the extract_attribute parameters are required; fill in every one of them. "
        "If there is no answer for a given parameter, fill it in with a blank string."
        )
    functions = [
        {
            "name": "extract_attributes",
            "description": "Add the attributes of a transcript to the database.",
            "parameters": {
                "type": "object",
                    "properties": {
                        "health_sector_discussed": {
                            "type": "string",
                            "description": "Was the health sector discussed at any point during this transcript? Yes or No."
                        },
                        "health_sector_discussed_people_names": {
                            "type": "string",
                            "description": "The names of the people that participated in discussions about the health sector during the transcript. Just their names, comma separated."
                        },
                        "health_data_information_systems_discussed": {
                            "type": "string",
                            "description": "Were there discussions about health data or health information systems at any point during this transcript? Yes or No."
                        },
                        "health_data_information_systems_summary": {
                            "type": "string",
                            "description": "Summary of discussions about health data or health information systems, if any."
                        },
                        "health_data_challenges": {
                            "type": "string",
                            "description": "What challenges did the discussions around health data or health information systems identify, if any?"
                        },
                        "health_service_delivery_improvement_recommendations": {
                            "type": "string",
                            "description": "What recommendations were discussed to improve health service delivery, if any?"
                        },
                        "health_sector_decisions": {
                            "type": "string",
                            "description": "What decisions were made regarding financing the health sector, if any? If no decisions were discussed, write 'No decisions.'"
                        },
                        "health_evidence_base": {
                            "type": "string",
                            "description": "What evidence was used to inform any decisions or recommendations?"
                        },
                        "health_evidence_requested": {
                            "type": "string",
                            "description": "What health sector information was requested or demanded, and who was it requested from?"
                        },
                    },
                "required": [
                    "health_sector_discussed",
                    "health_sector_discussed_people_names",
                    "health_data_information_systems_discussed",
                    "health_data_information_systems_summary",
                    "health_data_challenges",
                    "health_service_delivery_improvement_recommendations",
                    "health_sector_decision",
                    "health_evidence_base",
                    "health_evidence_requested"
                    ],
            },
        }
    ]
    tokenizer = tiktoken.encoding_for_model(MODEL)
    all_files = glob("ke_texts/*.txt")

    all_file_full_text_list = list()
    for txt_file_path in tqdm(all_files):
        with open(txt_file_path, 'r') as txt_file:
            all_file_full_text_list.append(txt_file.read())

    if warn_user_about_tokens(tokenizer, all_file_full_text_list, other_prompts=json.dumps(functions)) == True:

        for txt_filename in tqdm(all_files):
            txt_basename = os.path.basename(txt_filename)
            txt_file_basename, _ = os.path.splitext(txt_basename)
            with open(txt_filename, "r") as txt_file:
                full_text = txt_file.read()

            batches = chunk_by_tokens(tokenizer, full_text, 10000)
            for batch_i, batch in enumerate(batches):
                json_outfile = os.path.join("ke_health_json_responses", "{}_{}.json".format(txt_file_basename, batch_i))
                if not os.path.exists(json_outfile):
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": "Please extract the attributes from the following transcript: {}".format(
                                batches[0]
                            )
                        }
                    ]
                    response = client.chat.completions.create(
                        model=MODEL,
                        functions=functions, messages=messages
                    )
                    function_args = json.loads(
                        response.choices[0].message.function_call.arguments
                    )
                    
                    with open(json_outfile, 'w', encoding='utf-8') as json_file:
                        json.dump(function_args, json_file, ensure_ascii=False, indent=4)
