# InvokeModel - Amazon Bedrock InvokeModel - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

InvokeModel - Amazon Bedrock 
InvokeModel - Amazon Bedrock 
Documentation Amazon Bedrock API Reference 
Request Syntax URI Request Parameters Request Body Response Syntax Response Elements Errors Examples See Also 

InvokeModel 

Invokes the specified Amazon Bedrock model to run inference using the prompt and inference parameters provided in the request body. 
 You use model inference to generate text, images, and embeddings. 

For example code, see Invoke model code examples . 

This operation requires permission for the bedrock:InvokeModel action. 

Important 

To deny all inference access to resources that you specify in the modelId field, you
 need to deny access to the bedrock:InvokeModel and bedrock:InvokeModelWithResponseStream actions. Doing this also denies
 access to the resource through the Converse API actions ( Converse and ConverseStream ). For more information see Deny access for inference on specific models . 

For troubleshooting some of the common errors you might encounter when using the InvokeModel API, 
 see Troubleshooting Amazon Bedrock API Error Codes in the Amazon Bedrock User Guide 

Request Syntax 
POST /model/ modelId /invoke HTTP/1.1
Content-Type: contentType Accept: accept X-Amzn-Bedrock-Trace: trace X-Amzn-Bedrock-GuardrailIdentifier: guardrailIdentifier X-Amzn-Bedrock-GuardrailVersion: guardrailVersion X-Amzn-Bedrock-PerformanceConfig-Latency: performanceConfigLatency X-Amzn-Bedrock-Service-Tier: serviceTier body 
URI Request Parameters 
The request uses the following URI parameters. 
accept 
The desired MIME type of the inference body in the response. The default value is application/json . 
contentType 
The MIME type of the input data in the request. You must specify application/json . 
guardrailIdentifier 
The unique identifier of the guardrail that you want to use. If you don't provide a value, no guardrail is applied
 to the invocation. 

An error will be thrown in the following situations. 

You don't provide a guardrail identifier but you specify the amazon-bedrock-guardrailConfig field in the request body. 

You enable the guardrail but the contentType isn't application/json . 

You provide a guardrail identifier, but guardrailVersion isn't specified. 

Length Constraints: Minimum length of 0. Maximum length of 2048. 

Pattern: (|([a-z0-9]+)|(arn:aws(-[^:]+)?:bedrock:[a-z0-9-] { 1,20}:[0-9] { 12}:guardrail/[a-z0-9]+)) 
guardrailVersion 
The version number for the guardrail. The value can also be DRAFT . 

Pattern: (|([1-9][0-9] { 0,7})|(DRAFT)) 
modelId 
Specifies the model or throughput with which to run inference, or the prompt resource to use in inference. The value depends on the resource that you use: 

If you use a base model, specify the model ID or its ARN. For a list of model IDs for base models, see Amazon Bedrock base model IDs (on-demand throughput) in the Amazon Bedrock User Guide. 

If you use an Amazon Bedrock Marketplace model, specify the ID or ARN of the marketplace endpoint that you created. For more information about Amazon Bedrock Marketplace and setting up an endpoint, see Amazon Bedrock Marketplace in the Amazon Bedrock User Guide. 

If you use an inference profile, specify the inference profile ID or its ARN. For a list of inference profile IDs, see Supported Regions and models for cross-region inference in the Amazon Bedrock User Guide. 

If you use a prompt created through Prompt management , specify the ARN of the prompt version. For more information, see Test a prompt using Prompt management . 

If you use a provisioned model, specify the ARN of the Provisioned Throughput. For more information, see Run inference using a Provisioned Throughput in the Amazon Bedrock User Guide. 

If you use a custom model, specify the ARN of the custom model deployment (for on-demand inference) or the ARN of your provisioned model (for Provisioned Throughput). 
 For more information, see Use a custom model in Amazon Bedrock in the Amazon Bedrock User Guide. 

If you use an imported model , specify the ARN of the imported model. You can get the model ARN from a successful call to CreateModelImportJob or from the Imported models page in the Amazon Bedrock console. 

Length Constraints: Minimum length of 1. Maximum length of 2048. 

Pattern: (arn:aws(-[^:]+)?:bedrock:[a-z0-9-] { 1,20}:(([0-9] { 12}:custom-model/[a-z0-9-] { 1,63}[.] { 1}[a-z0-9-] { 1,63}/[a-z0-9] { 12})|(:foundation-model/[a-z0-9-] { 1,63}[.] { 1}[a-z0-9-] { 1,63}([.:]?[a-z0-9-] { 1,63}))|([0-9] { 12}:imported-model/[a-z0-9] { 12})|([0-9] { 12}:provisioned-model/[a-z0-9] { 12})|([0-9] { 12}:custom-model-deployment/[a-z0-9] { 12})|([0-9] { 12}:(inference-profile|application-inference-profile)/[a-zA-Z0-9-:.]+)))|([a-z0-9-] { 1,63}[.] { 1}[a-z0-9-] { 1,63}([.:]?[a-z0-9-] { 1,63}))|(([0-9a-zA-Z][_-]?)+)|([a-zA-Z0-9-:.]+)$|(^(arn:aws(-[^:]+)?:bedrock:[a-z0-9-] { 1,20}:[0-9] { 12}:prompt/[0-9a-zA-Z] { 10}(?::[0-9] { 1,5})?))$|(^arn:aws:sagemaker:[a-z0-9-]+:[0-9] { 12}:endpoint/[a-zA-Z0-9-]+$)|(^arn:aws(-[^:]+)?:bedrock:([0-9a-z-] { 1,20}):([0-9] { 12}):(default-)?prompt-router/[a-zA-Z0-9-:.]+$) 

Required: Yes 
performanceConfigLatency 
Model performance settings for the request. 

Valid Values: standard | optimized 
serviceTier 
Specifies the processing tier type used for serving the request. 

Valid Values: priority | default | flex | reserved 
trace 
Specifies whether to enable or disable the Bedrock trace. If enabled, you can see the full Bedrock trace. 

Valid Values: ENABLED | DISABLED | ENABLED_FULL 

Request Body 
The request accepts the following binary data. 
body 
The prompt and inference parameters in the format specified in the contentType in the header. You must provide the body in JSON format. To see the format and content of the request and response bodies for different models, refer to Inference parameters . For more information, see Run inference in the Bedrock User Guide. 

Length Constraints: Minimum length of 0. Maximum length of 25000000. 

Response Syntax 
HTTP/1.1 200
Content-Type: contentType X-Amzn-Bedrock-PerformanceConfig-Latency: performanceConfigLatency X-Amzn-Bedrock-Service-Tier: serviceTier body 
Response Elements 
If the action is successful, the service sends back an HTTP 200 response. 

The response returns the following HTTP headers. 
contentType 
The MIME type of the inference result. 
performanceConfigLatency 
Model performance settings for the request. 

Valid Values: standard | optimized 
serviceTier 
Specifies the processing tier type used for serving the request. 

Valid Values: priority | default | flex | reserved 

The response returns the following as the HTTP body. 
body 
Inference response from the model in the format specified in the contentType header. To see the format and content of the request and response bodies for different models, refer to Inference parameters . 

Length Constraints: Minimum length of 0. Maximum length of 25000000. 

Errors 
For information about the errors that are common to all actions, see Common Errors . 
AccessDeniedException 
The request is denied because you do not have sufficient permissions to perform the requested action. For troubleshooting this error, 
 see AccessDeniedException in the Amazon Bedrock User Guide 

HTTP Status Code: 403 
InternalServerException 
An internal server error occurred. For troubleshooting this error, 
 see InternalFailure in the Amazon Bedrock User Guide 

HTTP Status Code: 500 
ModelErrorException 
The request failed due to an error while processing the model. 
originalStatusCode 
The original status code. 
resourceName 
The resource name. 

HTTP Status Code: 424 
ModelNotReadyException 
The model specified in the request is not ready to serve inference requests. The AWS SDK
 will automatically retry the operation up to 5 times. For information about configuring
 automatic retries, see Retry behavior in the AWS SDKs and Tools reference guide. 

HTTP Status Code: 429 
ModelTimeoutException 
The request took too long to process. Processing time exceeded the model timeout length. 

HTTP Status Code: 408 
ResourceNotFoundException 
The specified resource ARN was not found. For troubleshooting this error, 
 see ResourceNotFound in the Amazon Bedrock User Guide 

HTTP Status Code: 404 
ServiceQuotaExceededException 
Your request exceeds the service quota for your account. You can view your quotas at Viewing service quotas . You can resubmit your request later. 

HTTP Status Code: 400 
ServiceUnavailableException 
The service isn't currently available. For troubleshooting this error, 
 see ServiceUnavailable in the Amazon Bedrock User Guide 

HTTP Status Code: 503 
ThrottlingException 
Your request was denied due to exceeding the account quotas for Amazon Bedrock . For
 troubleshooting this error, see ThrottlingException in the Amazon Bedrock User Guide 

HTTP Status Code: 429 
ValidationException 
The input fails to satisfy the constraints specified by Amazon Bedrock . For troubleshooting this error, 
 see ValidationError in the Amazon Bedrock User Guide 

HTTP Status Code: 400 

Examples 
Run inference on a text model 
Send an invoke request to run inference on a Titan Text G1 - Express model. We set the accept parameter to accept any content type in the response. 

Sample Request 
POST https://bedrock-runtime.us-east-1.amazonaws.com/model/amazon.titan-text-express-v1/invoke

-H accept: */* 
-H content-type: application/json

Payload { "inputText": "Hello world"} 
Run inference on an image model 
In the following example, the request sets the accept parameter to image/png . 

Sample Request 
POST https://bedrock-runtime.us-east-1.amazonaws.com/model/stability.stable-diffusion-xl-v1/invoke

-H accept: image/png
-H content-type: application/json

Payload { "inputText": "Picture of a bird"} 
Use a guardrail 
This example shows how to use a guardrail with InvokeModel . 

Sample Request 
POST /model/modelId/invoke HTTP/1.1
Accept: accept
Content-Type: contentType
X-Amzn-Bedrock-GuardrailIdentifier: guardrailIdentifier
X-Amzn-Bedrock-GuardrailVersion: guardrailVersion
X-Amzn-Bedrock-GuardrailTrace: guardrailTrace
X-Amzn-Bedrock-Trace: trace

body

// body { "amazon-bedrock-guardrailConfig": { "tagSuffix": "string"
 }
} 
Example response 
This is an example response from InvokeModel when using a
 guardrail. 

Sample Request 
HTTP/1.1 200
Content-Type: contentType

body

// body { "amazon-bedrock-guardrailAction": "INTERVENED | NONE",
 "amazon-bedrock-trace": { "guardrails": { // Detailed guardrail trace 
 }
 }
} 
Use an inference profile in model invocation 
The following request calls the US Anthropic Claude 3.5 Sonnet inference profile to route traffic to the us-east-1 and us-west-2 regions. 

Sample Request 
POST /model/us.anthropic.claude-3-5-sonnet-20240620-v1:0/invoke HTTP/1.1 { "anthropic_version": "bedrock-2023-05-31",
 "max_tokens": 1024,
 "messages": [ { "role": "user",
 "content": [ { "type": "text",
 "text": "Hello world"
 }
 ]
 }
 ]
} 
See Also 
For more information about using this API in one of the language-specific AWS SDKs, see the following: 

AWS Command Line Interface V2 

AWS SDK for .NET V4 

AWS SDK for C++ 

AWS SDK for Go v2 

AWS SDK for Java V2 

AWS SDK for JavaScript V3 

AWS SDK for Kotlin 

AWS SDK for PHP V3 

AWS SDK for Python 

AWS SDK for Ruby V3 

Document Conventions 
GetAsyncInvoke 
InvokeModelWithBidirectionalStream 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
