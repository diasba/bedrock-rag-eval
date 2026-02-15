# InvokeModelWithResponseStream - Amazon Bedrock InvokeModelWithResponseStream - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

InvokeModelWithResponseStream - Amazon Bedrock 
InvokeModelWithResponseStream - Amazon Bedrock 
Documentation Amazon Bedrock API Reference 
Request Syntax URI Request Parameters Request Body Response Syntax Response Elements Errors Examples See Also 

InvokeModelWithResponseStream 

Invoke the specified Amazon Bedrock model to run inference using the prompt and inference parameters provided in the request body. The response is returned in a stream. 

To see if a model supports streaming, call GetFoundationModel and check the responseStreamingSupported field in the response. 

Note 

The AWS CLI doesn't support streaming operations in Amazon Bedrock, including InvokeModelWithResponseStream . 

For example code, see Invoke model with streaming code example . 

This operation requires permissions to perform the bedrock:InvokeModelWithResponseStream action. 

Important 

To deny all inference access to resources that you specify in the modelId field, you
 need to deny access to the bedrock:InvokeModel and bedrock:InvokeModelWithResponseStream actions. Doing this also denies
 access to the resource through the Converse API actions ( Converse and ConverseStream ). For more information see Deny access for inference on specific models . 

For troubleshooting some of the common errors you might encounter when using the InvokeModelWithResponseStream API, 
 see Troubleshooting Amazon Bedrock API Error Codes in the Amazon Bedrock User Guide 

Request Syntax 
POST /model/ modelId /invoke-with-response-stream HTTP/1.1
Content-Type: contentType X-Amzn-Bedrock-Accept: accept X-Amzn-Bedrock-Trace: trace X-Amzn-Bedrock-GuardrailIdentifier: guardrailIdentifier X-Amzn-Bedrock-GuardrailVersion: guardrailVersion X-Amzn-Bedrock-PerformanceConfig-Latency: performanceConfigLatency X-Amzn-Bedrock-Service-Tier: serviceTier body 
URI Request Parameters 
The request uses the following URI parameters. 
accept 
The desired MIME type of the inference body in the response. The default value is application/json . 
contentType 
The MIME type of the input data in the request. You must specify application/json . 
guardrailIdentifier 
The unique identifier of the guardrail that you want to use. If you don't provide a value, no guardrail is applied
 to the invocation. 

An error is thrown in the following situations. 

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
X-Amzn-Bedrock-Content-Type: contentType X-Amzn-Bedrock-PerformanceConfig-Latency: performanceConfigLatency X-Amzn-Bedrock-Service-Tier: serviceTier Content-type: application/json { " chunk ": { " bytes ": blob },
 " internalServerException ": { },
 " modelStreamErrorException ": { },
 " modelTimeoutException ": { },
 " serviceUnavailableException ": { },
 " throttlingException ": { },
 " validationException ": { }
} 
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

The following data is returned in JSON format by the service. 
chunk 
Content included in the response. 

Type: PayloadPart object 
internalServerException 
An internal server error occurred. Retry your request. 

Type: Exception 

HTTP Status Code: 500 
modelStreamErrorException 
An error occurred while streaming the response. Retry your request. 

Type: Exception 

HTTP Status Code: 424 
modelTimeoutException 
The request took too long to process. Processing time exceeded the model timeout length. 

Type: Exception 

HTTP Status Code: 408 
serviceUnavailableException 
The service isn't available. Try again later. 

Type: Exception 

HTTP Status Code: 503 
throttlingException 
Your request was throttled because of service-wide limitations. Resubmit your request later or in a different region. You can also purchase Provisioned Throughput to increase the rate or number of tokens you can process. 

Type: Exception 

HTTP Status Code: 429 
validationException 
Input validation failed. Check your request parameters and retry the request. 

Type: Exception 

HTTP Status Code: 400 

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
ModelStreamErrorException 
An error occurred while streaming the response. Retry your request. 
originalMessage 
The original message. 
originalStatusCode 
The original status code. 

HTTP Status Code: 424 
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
Run inference with streaming on a text model 
For streaming, you can set x-amzn-bedrock-accept-type in the header
 to contain the desired content type of the response. In this example, we set it to
 accept any content type. The default value is application/json . 

Sample Request 
POST https://bedrock-runtime.us-east-1.amazonaws.com/model/amazon.titan-text-express-v1/invoke-with-response-stream

-H accept: application/vnd.amazon.eventstream
-H content-type: application/json
-H x-amzn-bedrock-accept: */*

Payload { "inputText": "Hello world"} 
Example response 
For streaming, the content type in the response is always set to application/vnd.amazon.eventstream .
 The response includes an additional header (x-amzn-bedrock-content-type), which contains the actual content type of the response. 

Sample Request 
-H content-type: application/vnd.amazon.eventstream
-H x-amzn-bedrock-content-type: application/json

Payload (stream events)
<response chunk> 
Use a guardrail 
This examples show how to use a guardrail with InvokeModelWithResponseStream . 

POST /model/modelId/invoke-with-response-stream HTTP/1.1
X-Amzn-Bedrock-Accept: accept
Content-Type: contentType
X-Amzn-Bedrock-GuardrailIdentifier: guardrailIdentifier
X-Amzn-Bedrock-GuardrailVersion: guardrailVersion
X-Amzn-Bedrock-GuardrailTrace: guardrailTrace
X-Amzn-Bedrock-Trace: trace

body

// body { "amazon-bedrock-guardrailConfig": { "tagSuffix": "string",
 "streamProcessingMode": "string"
 }
} 
Example response 
This examples shows the response from a call to InvokeModelWithResponseStream when using a guardrail. 

HTTP/1.1 200
X-Amzn-Bedrock-Content-Type: contentType
Content-type: application/json

// chunk 1 { "completion": "...",
 "amazon-bedrock-guardrailAction": "INTERVENED | NONE"
}

// chunk 2 { "completion": "...",
 "amazon-bedrock-guardrailAction": "INTERVENED | NONE"
}

// last chunk { "completion": "...",
 "amazon-bedrock-guardrailAction": "INTERVENED | NONE",
 "amazon-bedrock-trace": { "guardrail": { ... // Detailed guardrail trace
 }
 }
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
InvokeModelWithBidirectionalStream 
ListAsyncInvokes 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
