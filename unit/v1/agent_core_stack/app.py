import json
import logging
import os

import boto3
import yaml
from bedrock_agentcore.runtime import BedrockAgentCoreApp

logger = logging.getLogger(__name__)
app = BedrockAgentCoreApp()
bedrock_client = boto3.client("bedrock-runtime")
lambda_client = boto3.client("lambda")

with open("config_query_rewrite.yaml") as fp:
    config_query_rewrite = yaml.safe_load(fp)
model_id = config_query_rewrite["model"]["id"]
max_tokens = config_query_rewrite["parameters"]["max_tokens"]
temperature = config_query_rewrite["parameters"]["temperature"]
embedding_lambda_name = os.environ["EMBEDDING_LAMBDA_NAME"]

def rewrite_query(prompt: str) -> str:
    """Cheap rewrite against AWS Bedrock model."""

    resp = bedrock_client.converse(
        modelId=model_id,
        system=[
            {"text": config_query_rewrite["prompts"]["system"]}
        ],
        messages=[
            {"role": "user", "content": [{"text": prompt}]}
        ],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    )
    rewritten_query = resp["output"]["message"]["content"][0]["text"].strip()
    logger.debug(f"Prompt \n{prompt}\nyielded query\n{rewritten_query}")

    return rewritten_query

def embed_query(query: str) -> str:
    """Super simple embedding step (placeholder)."""


@app.entrypoint
def invoke(payload, context=None):
    # AgentCore starter toolkit sends {"prompt": "..."} by default
    prompt = payload.get("prompt", "")
    query = rewrite_query(prompt)

    embedding_request_payload = {
        "sentences": [query]
    }  # Assume single intent for embedding purposes
    resp = lambda_client.invoke(
        FunctionName=embedding_lambda_name,
        InvocationType="RequestResponse",
        ClientContext=json.dumps(b"{}").encode("utf-8"),
        Payload=json.dumps(embedding_request_payload).encode("utf-8"),  # bytes
    )
    logger.debug(f"Response from embedding lambda is {resp=}")


    # resp = bedrock_client.converse(
    #     modelId=model_id,
    #     messages=[
    #         {"role": "user", "content": [{"text": prompt}]}
    #     ],
    #     inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    # )
    #
    # text = resp["output"]["message"]["content"][0]["text"]
    # return {"result": text}
    return {"result": query}

if __name__ == "__main__":
    app.run()
