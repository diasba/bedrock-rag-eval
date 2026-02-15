# Endpoints supported by Amazon Bedrock - Amazon Bedrock Endpoints supported by Amazon Bedrock - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Endpoints supported by Amazon Bedrock - Amazon Bedrock 
Endpoints supported by Amazon Bedrock - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Endpoints supported by Amazon Bedrock 

Amazon Bedrock supports various endpoints depending on whether you want to perform control plane operators or inference operations. 

Control Plane operations 

Amazon Bedrock control plane operations can be used with the endpoint: bedrock. { region}.amazonaws.com. It can be used for managing resources, such as listing available models , creating custom model jobs, and managing provisioned throughput . Read more on our control plane API here . 

Inference operations 

Amazon Bedrock supports the following primary two end points for performing inference programmatically: 

Endpoint Supported APIs Description 
bedrock-mantle. { region}.amazonaws.com Responses API / Chat Completions API Region-specific endpoints for making inference requests for models hosted in Amazon Bedrock using the OpenAI-compatible endpoints. 
bedrock-runtime. { region}.amazonaws.com InvokeModel / Converse / Chat Completions Region-specific endpoints for making inference requests for models hosted in Amazon Bedrock using the InvokeModel/Converse/Chat Completions APIs. Read more on Amazon Bedrock Runtime APIs here . 

Which service endpoint should you use for your inference? 

The endpoint you use depends on your use-case. 

Endpoint Features and Use Cases 
bedrock-mantle 
Supports OpenAI-compatible APIs ( Responses API , Chat Completions API ). 

Use for: Easily migrating from other models that use the OpenAI-compatible APIs. 

Features: Supports both client and server side tool use with Lambda functions and comes configured with ready-to-use tools in your applications. 

Recommended for: New users to Amazon Bedrock. 

bedrock-runtime 
Supports Amazon Bedrock native APIs ( Invoke API , Converse API ). Also supports the OpenAI-compatible Chat Completions API . 

Use for: Running any model supported by Amazon Bedrock. The Converse API provides a unified interface for interacting with all models in Amazon Bedrock and the Invoke API provides direct access to models with more ability to control the request and response format. You can also use Chat Completions API to interact with your models. 

Features: Supports only client-side tool use with Lambda functions and does not come pre-configured with ready-to-use tools. Allows you to track usage and costs when invoking a model. 

If you are new to Amazon Bedrock, we recommend you start with the bedrock-mantle endpoint. 

Document Conventions 
APIs 
API keys 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
