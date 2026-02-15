# How Amazon Bedrock Guardrails works - Amazon Bedrock How Amazon Bedrock Guardrails works - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-how.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

How Amazon Bedrock Guardrails works - Amazon Bedrock 
How Amazon Bedrock Guardrails works - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
How charges are calculated for using Amazon Bedrock Guardrails 

How Amazon Bedrock Guardrails works 

Amazon Bedrock Guardrails helps keep your generative AI applications safe by evaluating both user inputs
 and model responses. 

You can configure guardrails for your applications based on the following
 considerations: 

An account can have multiple guardrails, each with a different configuration
 and customized to a specific use case. 

A guardrail is a combination of multiple policies configured for prompts and
 response including; content filters, denied topics, sensitive information
 filters, word filters, and image content filters. 

A guardrail can be configured with a single policy, or a combination of
 multiple policies. 

A guardrail can be used with any text or image foundation model (FM) by
 referencing the guardrail during the model inference. 

You can use guardrails with Amazon Bedrock Agents and Amazon Bedrock Knowledge Bases. 

When using a guardrail in the InvokeModel , InvokeModelWithResponseStream , Converse , or ConverseStream operations, it works as follows during the inference
 call. (How this works depends on how you configure your policies to handle inputs and
 outputs.) 

The input is evaluated against the configured policies specified in the
 guardrail. Furthermore, for improved latency, the input is evaluated in parallel
 for each configured policy. 

If the input evaluation results in a guardrail intervention, a configured blocked message response is returned and the foundation
 model inference is discarded. 

If the input evaluation succeeds, the model response is then subsequently
 evaluated against the configured policies in the guardrail. 

If the response results in a guardrail intervention or violation, it will be
 overridden with pre-configured blocked messaging or masking of the sensitive information based on your
 policy configuration. 

If the response's evaluation succeeds, the response is returned to the
 application without any modifications. 

For information on Amazon Bedrock Guardrails pricing, see the Amazon Bedrock pricing . 

How charges are calculated for Amazon Bedrock Guardrails 
Charges for Amazon Bedrock Guardrails are incurred only for the policies configured in the guardrail.
 The price for each policy type is available at Amazon Bedrock
 Pricing . 

If a guardrail blocks the input prompt, you're charged for the guardrail
 evaluation. There are no charges for foundation model inference
 calls. 

If a guardrail blocks the model response, you're charged for guardrail's
 evaluation of the input prompt and the model response. In this case, you're
 charged for the foundation model inference calls, in addition to the model
 response that was generated prior to the guardrail's evaluation. 

If a guardrail doesn't block the input prompt and the model response,
 you're charged for guardrail's evaluation of the prompt and the model
 response, in addition to the foundation model inference. 

Document Conventions 
Bedrock Guardrails 
Supported Regions/models 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
