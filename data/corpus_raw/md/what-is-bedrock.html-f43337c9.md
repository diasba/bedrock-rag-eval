# Overview - Amazon Bedrock Overview - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Overview - Amazon Bedrock 
Overview - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
Quickstart Models supported What's new? Start Building 

Overview 

Amazon Bedrock is a fully managed service that provides secure, enterprise-grade access to high-performing foundation models from leading AI companies, enabling you to build and scale generative AI applications. 

Quickstart Responses API 

from openai import OpenAI

client = OpenAI()

response = client.responses.create(
 model="openai.gpt-oss-120b",
 input="Can you explain the features of Amazon Bedrock?"
 )
print(response) Chat Completions API 

from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
 model="openai.gpt-oss-120b",
 messages=[ { "role": "user", "content": "Can you explain the features of Amazon Bedrock?"}]
 )
print(response) Invoke API 

import json
import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')
response = client.invoke_model(
 modelId='anthropic.claude-opus-4-6-v1',
 body=json.dumps( { 'anthropic_version': 'bedrock-2023-05-31',
 'messages': [ { 'role': 'user', 'content': 'Can you explain the features of Amazon Bedrock?'}],
 'max_tokens': 1024
 })
 )
 print(json.loads(response['body'].read())) Converse API 

import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')
response = client.converse(
 modelId='anthropic.claude-opus-4-6-v1',
 messages=[ { 'role': 'user',
 'content': [ { 'text': 'Can you explain the features of Amazon Bedrock?'}]
 }
 ]
)
print(response) 
Read the Quickstart to write your first API call using Amazon Bedrock in under five minutes. 

Models supported 
Bedrock supports 100+ foundation models from industry-leading providers, including Amazon, Anthropic, DeepSeek, Moonshot AI, MiniMax, and OpenAI. 

Nova 2 Pro 

Claude Opus 4.6 

Deepseek 3.2 

Kimi K2.5 

MiniMax M2.1 

GPT-OSS-20B 

What's new? 

Six new open weight models : Amazon Bedrock now supports six new models spanning frontier reasoning and agentic coding: DeepSeek V3.2, MiniMax M2.1, GLM 4.7, GLM 4.7 Flash, Kimi K2.5, and Qwen3 Coder Next. 

Claude 4.6 now available : According to Anthropic, Opus 4.6 is their most intelligent model and the world's best model for coding, enterprise agents, and professional work. Read more here. 

Server-side tools : Amazon Bedrock now supports server-side tools in the Responses API using OpenAI API-compatible service endpoints. 

1-hour prompt caching duration : Amazon Bedrock now supports a 1-hour time-to-live (TTL) option for prompt caching for select Anthropic Claude models. 

NVIDIA Nemotron 3 Nano now available : NVIDIA Nemotron 3 Nano 30B A3B delivers high reasoning performance, native tool calling support, and extended context processing with 256k token context window. 

Start Building 

Explore the APIs supported by Amazon Bedrock and Endpoints supported by Amazon Bedrock supported by Amazon Bedrock. 

Build using the Submit prompts and generate responses with model inference operations provided by Amazon Bedrock. 

Customize your models to improve performance and quality. Customize your model to improve its performance for your use case 

Document Conventions 
Quickstart 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
