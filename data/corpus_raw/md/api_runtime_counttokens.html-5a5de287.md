# CountTokens - Amazon Bedrock CountTokens - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_CountTokens.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

CountTokens - Amazon Bedrock 
CountTokens - Amazon Bedrock 
Documentation Amazon Bedrock API Reference 
Request Syntax URI Request Parameters Request Body Response Syntax Response Elements Errors See Also 

CountTokens 

Returns the token count for a given inference request. This operation helps you estimate token usage before sending requests to foundation models by returning the token count that would be used if the same input were sent to the model in an inference request. 

Token counting is model-specific because different models use different tokenization strategies. The token count returned by this operation will match the token count that would be charged if the same input were sent to the model in an InvokeModel or Converse request. 

You can use this operation to: 

Estimate costs before sending inference requests. 

Optimize prompts to fit within token limits. 

Plan for token usage in your applications. 

This operation accepts the same input formats as InvokeModel and Converse , allowing you to count tokens for both raw text inputs and structured conversation formats. 

The following operations are related to CountTokens : 

InvokeModel - Sends inference requests to foundation models 

Converse - Sends conversation-based inference requests to foundation models 

Request Syntax 
POST /model/ modelId /count-tokens HTTP/1.1
Content-type: application/json { " input ": { ... }
} 
URI Request Parameters 
The request uses the following URI parameters. 
modelId 
The unique identifier or ARN of the foundation model to use for token counting. Each model processes tokens differently, so the token count is specific to the model you specify. 

Length Constraints: Minimum length of 1. Maximum length of 256. 

Pattern: [a-zA-Z_\.\-/0-9:]+ 

Required: Yes 

Request Body 
The request accepts the following data in JSON format. 
input 
The input for which to count tokens. The structure of this parameter depends on whether you're counting tokens for an InvokeModel or Converse request: 

For InvokeModel requests, provide the request body in the invokeModel field 

For Converse requests, provide the messages and system content in the converse field 

The input format must be compatible with the model specified in the modelId parameter. 

Type: CountTokensInput object 

Note: This object is a Union. Only one member of this object can be specified or returned. 

Required: Yes 

Response Syntax 
HTTP/1.1 200
Content-type: application/json { " inputTokens ": number } 
Response Elements 
If the action is successful, the service sends back an HTTP 200 response. 

The following data is returned in JSON format by the service. 
inputTokens 
The number of tokens in the provided input according to the specified model's tokenization rules. This count represents the number of input tokens that would be processed if the same input were sent to the model in an inference request. Use this value to estimate costs and ensure your inputs stay within model token limits. 

Type: Integer 

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
ResourceNotFoundException 
The specified resource ARN was not found. For troubleshooting this error, 
 see ResourceNotFound in the Amazon Bedrock User Guide 

HTTP Status Code: 404 
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
ConverseStream 
GetAsyncInvoke 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
