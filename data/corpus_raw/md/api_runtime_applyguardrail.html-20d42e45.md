# ApplyGuardrail - Amazon Bedrock ApplyGuardrail - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ApplyGuardrail.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

ApplyGuardrail - Amazon Bedrock 
ApplyGuardrail - Amazon Bedrock 
Documentation Amazon Bedrock API Reference 
Request Syntax URI Request Parameters Request Body Response Syntax Response Elements Errors See Also 

ApplyGuardrail 

The action to apply a guardrail. 

For troubleshooting some of the common errors you might encounter when using the ApplyGuardrail API, 
 see Troubleshooting Amazon Bedrock API Error Codes in the Amazon Bedrock User Guide 

Request Syntax 
POST /guardrail/ guardrailIdentifier /version/ guardrailVersion /apply HTTP/1.1
Content-type: application/json { " content ": [ { ... }
 ],
 " outputScope ": " string ",
 " source ": " string "
} 
URI Request Parameters 
The request uses the following URI parameters. 
guardrailIdentifier 
The guardrail identifier used in the request to apply the guardrail. 

Length Constraints: Minimum length of 0. Maximum length of 2048. 

Pattern: (|([a-z0-9]+)|(arn:aws(-[^:]+)?:bedrock:[a-z0-9-] { 1,20}:[0-9] { 12}:guardrail/[a-z0-9]+)) 

Required: Yes 
guardrailVersion 
The guardrail version used in the request to apply the guardrail. 

Pattern: (|([1-9][0-9] { 0,7})|(DRAFT)) 

Required: Yes 

Request Body 
The request accepts the following data in JSON format. 
content 
The content details used in the request to apply the guardrail. 

Type: Array of GuardrailContentBlock objects 

Required: Yes 
outputScope 
Specifies the scope of the output that you get in the response. Set to FULL to return the entire output, including any detected and non-detected entries in the response for enhanced debugging. 

Note that the full output scope doesn't apply to word filters or regex in sensitive information filters. It does apply to all other filtering policies, including sensitive information with filters that can detect personally identifiable information (PII). 

Type: String 

Valid Values: INTERVENTIONS | FULL 

Required: No 
source 
The source of data used in the request to apply the guardrail. 

Type: String 

Valid Values: INPUT | OUTPUT 

Required: Yes 

Response Syntax 
HTTP/1.1 200
Content-type: application/json { " action ": " string ",
 " actionReason ": " string ",
 " assessments ": [ { " appliedGuardrailDetails ": { " guardrailArn ": " string ",
 " guardrailId ": " string ",
 " guardrailOrigin ": [ " string " ],
 " guardrailOwnership ": " string ",
 " guardrailVersion ": " string "
 },
 " automatedReasoningPolicy ": { " findings ": [ { ... }
 ]
 },
 " contentPolicy ": { " filters ": [ { " action ": " string ",
 " confidence ": " string ",
 " detected ": boolean ,
 " filterStrength ": " string ",
 " type ": " string "
 }
 ]
 },
 " contextualGroundingPolicy ": { " filters ": [ { " action ": " string ",
 " detected ": boolean ,
 " score ": number ,
 " threshold ": number ,
 " type ": " string "
 }
 ]
 },
 " invocationMetrics ": { " guardrailCoverage ": { " images ": { " guarded ": number ,
 " total ": number },
 " textCharacters ": { " guarded ": number ,
 " total ": number }
 },
 " guardrailProcessingLatency ": number ,
 " usage ": { " automatedReasoningPolicies ": number ,
 " automatedReasoningPolicyUnits ": number ,
 " contentPolicyImageUnits ": number ,
 " contentPolicyUnits ": number ,
 " contextualGroundingPolicyUnits ": number ,
 " sensitiveInformationPolicyFreeUnits ": number ,
 " sensitiveInformationPolicyUnits ": number ,
 " topicPolicyUnits ": number ,
 " wordPolicyUnits ": number }
 },
 " sensitiveInformationPolicy ": { " piiEntities ": [ { " action ": " string ",
 " detected ": boolean ,
 " match ": " string ",
 " type ": " string "
 }
 ],
 " regexes ": [ { " action ": " string ",
 " detected ": boolean ,
 " match ": " string ",
 " name ": " string ",
 " regex ": " string "
 }
 ]
 },
 " topicPolicy ": { " topics ": [ { " action ": " string ",
 " detected ": boolean ,
 " name ": " string ",
 " type ": " string "
 }
 ]
 },
 " wordPolicy ": { " customWords ": [ { " action ": " string ",
 " detected ": boolean ,
 " match ": " string "
 }
 ],
 " managedWordLists ": [ { " action ": " string ",
 " detected ": boolean ,
 " match ": " string ",
 " type ": " string "
 }
 ]
 }
 }
 ],
 " guardrailCoverage ": { " images ": { " guarded ": number ,
 " total ": number },
 " textCharacters ": { " guarded ": number ,
 " total ": number }
 },
 " outputs ": [ { " text ": " string "
 }
 ],
 " usage ": { " automatedReasoningPolicies ": number ,
 " automatedReasoningPolicyUnits ": number ,
 " contentPolicyImageUnits ": number ,
 " contentPolicyUnits ": number ,
 " contextualGroundingPolicyUnits ": number ,
 " sensitiveInformationPolicyFreeUnits ": number ,
 " sensitiveInformationPolicyUnits ": number ,
 " topicPolicyUnits ": number ,
 " wordPolicyUnits ": number }
} 
Response Elements 
If the action is successful, the service sends back an HTTP 200 response. 

The following data is returned in JSON format by the service. 
action 
The action taken in the response from the guardrail. 

Type: String 

Valid Values: NONE | GUARDRAIL_INTERVENED 
actionReason 
The reason for the action taken when harmful content is detected. 

Type: String 
assessments 
The assessment details in the response from the guardrail. 

Type: Array of GuardrailAssessment objects 
guardrailCoverage 
The guardrail coverage details in the apply guardrail response. 

Type: GuardrailCoverage object 
outputs 
The output details in the response from the guardrail. 

Type: Array of GuardrailOutputContent objects 
usage 
The usage details in the response from the guardrail. 

Type: GuardrailUsage object 

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
Amazon Bedrock Runtime 
Converse 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
