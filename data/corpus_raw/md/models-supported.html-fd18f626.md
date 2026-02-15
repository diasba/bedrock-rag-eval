# Supported foundation models in Amazon Bedrock - Amazon Bedrock Supported foundation models in Amazon Bedrock - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Supported foundation models in Amazon Bedrock - Amazon Bedrock 
Supported foundation models in Amazon Bedrock - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Supported foundation models in Amazon Bedrock 

The table below lists information for foundation models supported by Amazon Bedrock. The following list describes the columns in the table: 

Provider – The model provider. 

Model – The name of the foundation model. 

Model ID – The AWS Region-agnostic ID of the model. Used in inference operations. 

Single-region model support – The AWS Regions that support inference calls to the model in that single Region. For more information, see Submit prompts and generate responses with model inference . 

Cross-region inference profile support – The AWS Regions that support inference calls to multiple Regions within the same geographical area. For more information, see Supported Regions and models for inference profiles . 

Input modalities – The modalities that can be provided as input to the model in inference. 

Output modalities – The modalities that can be output from the model in inference. 

Streaming – Whether the model supports streaming operations, such as InvokeModelWithResponseStream and ConverseStream . 

Inference parameters – A link to the inference parameters that you can specify when invoking the model. 

Provider Model Model ID Single-region model support Cross-region inference profile support Input modalities Output modalities Streaming Inference parameters 
AI21 Labs Jamba 1.5 Large ai21.jamba-1-5-large-v1:0 
us-east-1 

Text 

Text 
Yes Link 
AI21 Labs Jamba 1.5 Mini ai21.jamba-1-5-mini-v1:0 
us-east-1 

Text 

Text 
Yes Link 
Amazon Amazon Nova Multimodal Embeddings amazon.nova-2-multimodal-embeddings-v1:0 
us-east-1 

Text 

Image 

Audio 

Video 

Embedding 
No Link 
Amazon Nova 2 Lite amazon.nova-2-lite-v1:0 
ap-east-2 

ap-northeast-1 

ap-northeast-2 

ap-south-1 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ap-southeast-5 

ap-southeast-7 

ca-central-1 

ca-west-1 

eu-central-1 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-2 

eu-west-3 

il-central-1 

me-central-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Image 

Video 

Text 
Yes N/A 
Amazon Nova 2 Sonic amazon.nova-2-sonic-v1:0 
ap-northeast-1 

eu-north-1 

us-east-1 

us-west-2 

Speech 

Speech 

Text 
Yes N/A 
Amazon Nova Canvas amazon.nova-canvas-v1:0 
ap-northeast-1 

eu-west-1 

us-east-1 

Text 

Image 

Image 
No Link 
Amazon Nova Lite amazon.nova-lite-v1:0 
ap-northeast-1 

ap-southeast-2 

ap-southeast-3 

eu-north-1 

eu-west-2 

me-central-1 

us-east-1 

us-gov-west-1 

ap-east-2 

ap-northeast-1 

ap-northeast-2 

ap-south-1 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ap-southeast-5 

ap-southeast-7 

ca-central-1 

ca-west-1 

eu-central-1 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-3 

il-central-1 

me-central-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Image 

Video 

Text 
Yes Link 
Amazon Nova Micro amazon.nova-micro-v1:0 
ap-southeast-2 

eu-west-2 

us-east-1 

us-gov-west-1 

ap-east-2 

ap-northeast-1 

ap-northeast-2 

ap-south-1 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-5 

ap-southeast-7 

eu-central-1 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-3 

il-central-1 

me-central-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Amazon Nova Premier amazon.nova-premier-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Video 

Text 
Yes Link 
Amazon Nova Pro amazon.nova-pro-v1:0 
ap-southeast-2 

ap-southeast-3 

eu-west-2 

me-central-1 

us-east-1 

us-gov-west-1 

ap-east-2 

ap-northeast-1 

ap-northeast-2 

ap-south-1 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ap-southeast-5 

ap-southeast-7 

eu-central-1 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-3 

il-central-1 

me-central-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Image 

Video 

Text 
Yes Link 
Amazon Nova Reel amazon.nova-reel-v1:0 
ap-northeast-1 

eu-west-1 

us-east-1 

Text 

Image 

Video 
No Link 
Amazon Nova Reel amazon.nova-reel-v1:1 
us-east-1 

Text 

Image 

Video 
No Link 
Amazon Nova Sonic amazon.nova-sonic-v1:0 
ap-northeast-1 

eu-north-1 

us-east-1 

Speech 

Speech 

Text 
Yes Link 
Amazon Rerank 1.0 amazon.rerank-v1:0 
ap-northeast-1 

ca-central-1 

eu-central-1 

us-west-2 

Text 

Text 
No N/A 
Amazon Titan Embeddings G1 - Text amazon.titan-embed-text-v1 
ap-northeast-1 

eu-central-1 

us-east-1 

us-west-2 

Text 

Embedding 
No Link 
Amazon Titan Image Generator G1 v2 amazon.titan-image-generator-v2:0 
us-east-1 

us-west-2 

Text 

Image 

Image 
No Link 
Amazon Titan Multimodal Embeddings G1 amazon.titan-embed-image-v1 
ap-south-1 

ap-southeast-2 

ca-central-1 

eu-central-1 

eu-west-1 

eu-west-2 

eu-west-3 

sa-east-1 

us-east-1 

us-west-2 

Text 

Image 

Embedding 
No Link 
Amazon Titan Text Embeddings V2 amazon.titan-embed-text-v2:0 
ap-northeast-1 

ap-northeast-2 

ap-northeast-3 

ap-south-1 

ap-south-2 

ap-southeast-2 

ca-central-1 

eu-central-1 

eu-central-2 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-2 

eu-west-3 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

us-gov-west-1 

us-gov-east-1 

Text 

Embedding 
No Link 
Amazon Titan Text Embeddings v2 amazon.titan-embed-g1-text-02 
us-east-1 

us-west-2 

Text 

Embedding 
No N/A 
Amazon Titan Text Large amazon.titan-tg1-large 
us-east-1 

us-west-2 

Text 

Text 
Yes Link 
Anthropic Claude 3 Haiku anthropic.claude-3-haiku-20240307-v1:0 
ap-northeast-1 

ap-northeast-2 

ap-south-1 

ap-southeast-1 

ap-southeast-2 

ca-central-1 

eu-central-1 

eu-central-2 

eu-west-1 

eu-west-2 

eu-west-3 

me-central-1 

sa-east-1 

us-east-1 

us-west-2 

us-gov-west-1 

eu-central-1 

us-east-2 

us-gov-east-1 

Text 

Image 

Text 
Yes Link 
Anthropic Claude 3.5 Haiku anthropic.claude-3-5-haiku-20241022-v1:0 
me-central-1 

us-west-2 

us-east-1 

us-east-2 

Text 

Text 
Yes Link 
Anthropic Claude Haiku 4.5 anthropic.claude-haiku-4-5-20251001-v1:0 
ap-northeast-1 

ap-northeast-2 

ap-northeast-3 

ap-south-1 

ap-south-2 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ca-central-1 

eu-central-1 

eu-central-2 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-2 

eu-west-3 

me-central-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Image 

Text 
Yes Link 
Anthropic Claude Opus 4.1 anthropic.claude-opus-4-1-20250805-v1:0 
me-central-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes Link 
Anthropic Claude Opus 4.5 anthropic.claude-opus-4-5-20251101-v1:0 
ap-northeast-1 

ap-northeast-2 

ap-northeast-3 

ap-south-1 

ap-south-2 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ca-central-1 

eu-central-1 

eu-central-2 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-2 

eu-west-3 

me-central-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Image 

Text 
Yes Link 
Anthropic Claude Opus 4.6 anthropic.claude-opus-4-6-v1 
af-south-1 

ap-east-2 

ap-northeast-1 

ap-northeast-2 

ap-northeast-3 

ap-south-1 

ap-south-2 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ap-southeast-5 

ap-southeast-7 

ca-central-1 

ca-west-1 

eu-central-1 

eu-central-2 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-2 

eu-west-3 

il-central-1 

me-central-1 

me-south-1 

mx-central-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

Image 

Text 

Text 
Yes Link 
Anthropic Claude Sonnet 4.5 anthropic.claude-sonnet-4-5-20250929-v1:0 
af-south-1 

ap-northeast-1 

ap-northeast-2 

ap-northeast-3 

ap-south-1 

ap-south-2 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ca-central-1 

ca-west-1 

eu-central-1 

eu-central-2 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-2 

eu-west-3 

me-south-1 

mx-central-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

us-gov-west-1 

us-gov-east-1 

Text 

Image 

Text 
Yes Link 
Anthropic Claude Sonnet 4 anthropic.claude-sonnet-4-20250514-v1:0 
ap-east-2 

ap-northeast-1 

ap-northeast-2 

ap-northeast-3 

ap-south-1 

ap-south-2 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ap-southeast-5 

ap-southeast-7 

eu-central-1 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-3 

il-central-1 

me-central-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Image 

Text 
Yes Link 
Cohere Command R+ cohere.command-r-plus-v1:0 
us-east-1 

us-west-2 

Text 

Text 
Yes Link 
Cohere Command R cohere.command-r-v1:0 
us-east-1 

us-west-2 

Text 

Text 
Yes Link 
Cohere Embed English cohere.embed-english-v3 
ap-northeast-1 

ap-south-1 

ap-southeast-1 

ap-southeast-2 

ca-central-1 

eu-central-1 

eu-west-1 

eu-west-2 

eu-west-3 

sa-east-1 

us-east-1 

us-west-2 

Text 

Embedding 
No Link 
Cohere Embed Multilingual cohere.embed-multilingual-v3 
ap-northeast-1 

ap-south-1 

ap-southeast-1 

ap-southeast-2 

ca-central-1 

eu-central-1 

eu-west-1 

eu-west-2 

eu-west-3 

sa-east-1 

us-east-1 

us-west-2 

Text 

Embedding 
No Link 
Cohere Embed v4 cohere.embed-v4:0 
ap-northeast-1 

eu-west-1 

us-east-1 

ap-northeast-1 

ap-northeast-2 

ap-northeast-3 

ap-south-1 

ap-south-2 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ca-central-1 

eu-central-1 

eu-central-2 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-2 

eu-west-3 

me-central-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Image 

Embedding 
No Link 
Cohere Rerank 3.5 cohere.rerank-v3-5:0 
ap-northeast-1 

ca-central-1 

eu-central-1 

us-east-1 

us-west-2 

Text 

Text 
No Link 
DeepSeek DeepSeek-R1 deepseek.r1-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
DeepSeek DeepSeek-V3.1 deepseek.v3-v1:0 
ap-northeast-1 

ap-south-1 

ap-southeast-3 

eu-north-1 

eu-west-2 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Google Gemma 3 12B IT google.gemma-3-12b-it 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes N/A 
Google Gemma 3 27B PT google.gemma-3-27b-it 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes N/A 
Google Gemma 3 4B IT google.gemma-3-4b-it 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes N/A 
Luma AI Ray v2 luma.ray-v2:0 
us-west-2 

Text 

Video 
No Link 
Meta Llama 3 70B Instruct meta.llama3-70b-instruct-v1:0 
ap-south-1 

ca-central-1 

eu-west-2 

us-east-1 

us-west-2 

us-gov-west-1 

Text 

Text 
Yes Link 
Meta Llama 3 8B Instruct meta.llama3-8b-instruct-v1:0 
ap-south-1 

ca-central-1 

eu-west-2 

us-east-1 

us-west-2 

us-gov-west-1 

Text 

Text 
Yes Link 
Meta Llama 3.1 405B Instruct meta.llama3-1-405b-instruct-v1:0 
us-west-2 

us-east-2 

Text 

Text 
Yes Link 
Meta Llama 3.1 70B Instruct meta.llama3-1-70b-instruct-v1:0 
us-west-2 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Meta Llama 3.1 8B Instruct meta.llama3-1-8b-instruct-v1:0 
us-west-2 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Meta Llama 3.2 11B Instruct meta.llama3-2-11b-instruct-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes Link 
Meta Llama 3.2 1B Instruct meta.llama3-2-1b-instruct-v1:0 
eu-central-1 

eu-west-1 

eu-west-3 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Meta Llama 3.2 3B Instruct meta.llama3-2-3b-instruct-v1:0 
eu-central-1 

eu-west-1 

eu-west-3 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Meta Llama 3.2 90B Instruct meta.llama3-2-90b-instruct-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes Link 
Meta Llama 3.3 70B Instruct meta.llama3-3-70b-instruct-v1:0 
us-east-2 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Meta Llama 4 Maverick 17B Instruct meta.llama4-maverick-17b-instruct-v1:0 
us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Image 

Text 
Yes Link 
Meta Llama 4 Scout 17B Instruct meta.llama4-scout-17b-instruct-v1:0 
us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Image 

Text 
Yes Link 
MiniMax MiniMax M2 minimax.minimax-m2 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes N/A 
Mistral AI Magistral Small 2509 mistral.magistral-small-2509 
ap-northeast-1 

ap-south-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes N/A 
Mistral AI Ministral 14B 3.0 mistral.ministral-3-14b-instruct 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes N/A 
Mistral AI Ministral 3 8B mistral.ministral-3-8b-instruct 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes N/A 
Mistral AI Ministral 3B mistral.ministral-3-3b-instruct 
ap-northeast-1 

ap-south-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes N/A 
Mistral AI Mistral 7B Instruct mistral.mistral-7b-instruct-v0:2 
ap-south-1 

ap-southeast-2 

ca-central-1 

eu-west-1 

eu-west-2 

eu-west-3 

sa-east-1 

us-east-1 

us-west-2 

Text 

Text 
Yes Link 
Mistral AI Mistral Large (24.02) mistral.mistral-large-2402-v1:0 
ap-south-1 

ap-southeast-2 

ca-central-1 

eu-west-1 

eu-west-2 

eu-west-3 

sa-east-1 

us-east-1 

us-west-2 

Text 

Text 
Yes Link 
Mistral AI Mistral Large (24.07) mistral.mistral-large-2407-v1:0 
us-west-2 

Text 

Text 
Yes Link 
Mistral AI Mistral Large 3 mistral.mistral-large-3-675b-instruct 
ap-northeast-1 

ap-south-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes N/A 
Mistral AI Mistral Small (24.02) mistral.mistral-small-2402-v1:0 
us-east-1 

Text 

Text 
Yes Link 
Mistral AI Mixtral 8x7B Instruct mistral.mixtral-8x7b-instruct-v0:1 
ap-south-1 

ap-southeast-2 

ca-central-1 

eu-west-1 

eu-west-2 

eu-west-3 

sa-east-1 

us-east-1 

us-west-2 

Text 

Text 
Yes Link 
Mistral AI Pixtral Large (25.02) mistral.pixtral-large-2502-v1:0 
eu-central-1 

eu-north-1 

eu-west-1 

eu-west-3 

us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes Link 
Mistral AI Voxtral Mini 3B 2507 mistral.voxtral-mini-3b-2507 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Speech 

Text 

Text 
Yes N/A 
Mistral AI Voxtral Small 24B 2507 mistral.voxtral-small-24b-2507 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Speech 

Text 

Text 
Yes N/A 
Moonshot AI Kimi K2 Thinking moonshot.kimi-k2-thinking 
ap-northeast-1 

ap-south-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes N/A 
NVIDIA NVIDIA Nemotron Nano 12B v2 VL BF16 nvidia.nemotron-nano-12b-v2 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes N/A 
NVIDIA NVIDIA Nemotron Nano 9B v2 nvidia.nemotron-nano-9b-v2 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes N/A 
OpenAI GPT OSS Safeguard 120B openai.gpt-oss-safeguard-120b 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes N/A 
OpenAI GPT OSS Safeguard 20B openai.gpt-oss-safeguard-20b 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes N/A 
OpenAI gpt-oss-120b openai.gpt-oss-120b-1:0 
ap-northeast-1 

ap-south-1 

ap-southeast-3 

eu-central-1 

eu-north-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
OpenAI gpt-oss-20b openai.gpt-oss-20b-1:0 
ap-northeast-1 

ap-south-1 

ap-southeast-3 

eu-central-1 

eu-north-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Qwen Qwen3 235B A22B 2507 qwen.qwen3-235b-a22b-2507-v1:0 
ap-northeast-1 

ap-south-1 

ap-southeast-3 

eu-central-1 

eu-north-1 

eu-south-1 

eu-west-2 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Qwen Qwen3 32B (dense) qwen.qwen3-32b-v1:0 
ap-northeast-1 

ap-south-1 

ap-southeast-3 

eu-central-1 

eu-north-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Qwen Qwen3 Coder 480B A35B Instruct qwen.qwen3-coder-480b-a35b-v1:0 
ap-northeast-1 

ap-south-1 

ap-southeast-3 

eu-north-1 

eu-west-2 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Qwen Qwen3 Next 80B A3B qwen.qwen3-next-80b-a3b 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes N/A 
Qwen Qwen3 VL 235B A22B qwen.qwen3-vl-235b-a22b 
ap-northeast-1 

ap-south-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Text 
Yes N/A 
Qwen Qwen3-Coder-30B-A3B-Instruct qwen.qwen3-coder-30b-a3b-v1:0 
ap-northeast-1 

ap-south-1 

ap-southeast-3 

eu-central-1 

eu-north-1 

eu-south-1 

eu-west-1 

eu-west-2 

sa-east-1 

us-east-1 

us-east-2 

us-west-2 

Text 

Text 
Yes Link 
Stability AI Stable Diffusion 3.5 Large stability.sd3-5-large-v1:0 
us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Conservative Upscale stability.stable-conservative-upscale-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Control Sketch stability.stable-image-control-sketch-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Control Structure stability.stable-image-control-structure-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Core 1.0 stability.stable-image-core-v1:1 
us-west-2 

Text 

Image 
No Link 
Stability AI Stable Image Creative Upscale stability.stable-creative-upscale-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Erase Object stability.stable-image-erase-object-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Fast Upscale stability.stable-fast-upscale-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Inpaint stability.stable-image-inpaint-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Outpaint stability.stable-outpaint-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Remove Background stability.stable-image-remove-background-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Search and Recolor stability.stable-image-search-recolor-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Search and Replace stability.stable-image-search-replace-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Style Guide stability.stable-image-style-guide-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Style Transfer stability.stable-style-transfer-v1:0 
us-east-1 

us-east-2 

us-west-2 

Text 

Image 

Image 
No Link 
Stability AI Stable Image Ultra 1.0 stability.stable-image-ultra-v1:1 
us-west-2 

Text 

Image 
No Link 
TwelveLabs Marengo Embed 3.0 twelvelabs.marengo-embed-3-0-v1:0 
ap-northeast-2 

us-east-1 

eu-west-1 

us-east-1 

Text 

Image 

Speech 

Video 

Embedding 
No Link 
TwelveLabs Marengo Embed v2.7 twelvelabs.marengo-embed-2-7-v1:0 
ap-northeast-2 

eu-west-1 

us-east-1 

Text 

Image 

Speech 

Video 

Embedding 
No Link 
TwelveLabs Pegasus v1.2 twelvelabs.pegasus-1-2-v1:0 
ap-northeast-2 

us-east-1 

af-south-1 

ap-east-2 

ap-northeast-1 

ap-northeast-2 

ap-northeast-3 

ap-south-1 

ap-south-2 

ap-southeast-1 

ap-southeast-2 

ap-southeast-3 

ap-southeast-4 

ap-southeast-5 

ap-southeast-7 

ca-central-1 

ca-west-1 

eu-central-1 

eu-central-2 

eu-north-1 

eu-south-1 

eu-south-2 

eu-west-1 

eu-west-2 

eu-west-3 

il-central-1 

me-central-1 

me-south-1 

mx-central-1 

sa-east-1 

us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Video 

Text 
Yes Link 
Writer Palmyra X4 writer.palmyra-x4-v1:0 
us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Text 
Yes Link 
Writer Palmyra X5 writer.palmyra-x5-v1:0 
us-east-1 

us-east-2 

us-west-1 

us-west-2 

Text 

Text 
Yes Link 

The following models are also supported by Amazon Bedrock: 

Provider Model Model ID 
Qwen Qwen3 Next 80B A3B Instruct qwen.qwen3-next-80b-a3b 
Qwen Qwen3 VL 235B A22B qwen.qwen3-vl-235b-a22b 
OpenAI GPT OSS Safeguard 20B openai.gpt-oss-safeguard-20b 
OpenAI GPT OSS Safeguard 120B openai.gpt-oss-safeguard-120b 
Google Gemma 3 4B IT google.gemma-3-4b-it 
Google Gemma 3 12B IT google.gemma-3-12b-it 
Google Gemma 3 27B IT google.gemma-3-27b-it 
MiniMax MiniMax M2 minimax.minimax-m2 
Moonshot AI Kimi K2 Thinking moonshot.kimi-k2-thinking 
NVIDIA NVIDIA Nemotron Nano 9B v2 nvidia.nemotron-nano-9b-v2 
NVIDIA NVIDIA Nemotron Nano 12B v2 VL BF16 nvidia.nemotron-nano-12b-v2 
Mistral AI Magistral Small 2509 mistral.magistral-small-2509 
Mistral AI Voxtral Mini 3B 2507 mistral.voxtral-mini-3b-2507 
Mistral AI Voxtral Small 24B 2507 mistral.voxtral-small-24b-2507 
Mistral Ministral 3B mistral.ministral-3-3b-instruct 
Mistral Ministral 3 8B mistral.ministral-3-8b-instruct 
Mistral Ministral 3 14B mistral.ministral-3-14b-instruct 
Mistral Mistral Large 3 mistral.mistral-large-3-675b-instruct 

Certain models have a targeted date for deprecation. For more information, see Model lifecycle . 

To learn more about a provider, navigate to the following links: 

Amazon Nova 

AI21 Labs 

Anthropic 

Cohere 

DeepSeek 

Luma AI 

Meta 

Mistral AI 

OpenAI 

Qwen 

Stability AI 

TwelveLabs 

Writer AI 

Document Conventions 
Get model information 
Model support by Region 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
