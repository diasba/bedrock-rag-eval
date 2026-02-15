# Quickstart - Amazon Bedrock Quickstart - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Quickstart - Amazon Bedrock 
Quickstart - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Quickstart 

In this section, we will show you how to get started with Amazon Bedrock within a few minutes. We will use the OpenAI-compatible APIs: Responses API and Chat Completions API , and the Invoke and Converse API to show you how run an inference request. See Build for list of complete APIs. 

Step 1 - AWS Account: If you have an AWS account already, skip this step and go to step 2. If you are new to AWS, sign up for an AWS account and follow instructions. 

Step 2 - API key: Once you have an AWS account, you can create a long-term API key to authenticate your requests to Amazon Bedrock. To do that, go to the Amazon Bedrock service in AWS Console and generate a long term key. For more information, see the API keys section in the Build chapter. 

Step 3 - Get the SDK: To use this getting started guide, you must have Python already installed. Then install the relevant software depending on the APIs you are using. 
Responses/Chat Completions API 

pip install boto3 openai Invoke/Converse API 

pip install boto3 
Step 4 - Set environment variables: Configure your environment to use the API key for authentication. 
Responses/Chat Completions API 

OPENAI_API_KEY="<provide your long term key>" OPENAI_BASE_URL="https://bedrock-mantle.<your-region>.api.aws/v1" Invoke/Converse API 

AWS_BEARER_TOKEN_BEDROCK="<provide your long term key>" 
Step 5 - Run your first inference request: Amazon Bedrock supports 100+ foundation models . Choose a model, and then use the following Python code to run your first inference request. Save the file as bedrock-first-request.py 
Responses API 

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
Execute the code with Python by using the command: 

python3 bedrock-first-request.py 
You should see the output of your inference request. 

To learn more about using other APIs and endpoints, please refer to Build . 

Document Conventions 
Overview 
Models 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
