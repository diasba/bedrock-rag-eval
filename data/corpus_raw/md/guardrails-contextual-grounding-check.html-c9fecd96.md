# Use contextual grounding check to filter hallucinations in responses - Amazon Bedrock Use contextual grounding check to filter hallucinations in responses - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Use contextual grounding check to filter hallucinations in responses - Amazon Bedrock 
Use contextual grounding check to filter hallucinations in responses - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
Add contextual grounding
 checks with the console Calling contextual
 grounding check with Invoke APIs Calling contextual
 grounding check with Converse APIs Calling
 contextual grounding check with ApplyGuardrail API 

Use contextual grounding check
 to filter hallucinations in responses 

Amazon Bedrock Guardrails supports contextual grounding checks to detect and filter hallucinations in model
 responses when a reference source and a user query is provided. The supported use cases
 include summarization, paraphrasing, and question answering as defined in computer
 science discipline. (Conversational QA / Chatbot use cases are not supported.) 

Contextual grounding checks check for relevance for each chunk processed. If any one
 chunk is deemed relevant, the whole response is considered relevant as it has the answer
 to user’s query. For streaming API, this can result in scenario where an irrelevant
 response is returned to the user and is only marked as irrelevant after the whole
 response is streamed. 

Contextual grounding checks the following paradigms: 

Grounding – This checks if the model
 response is factually accurate based on the source and is grounded in the
 source. Any new information introduced in the response will be considered
 un-grounded. 

Relevance – This checks if the model
 response is relevant to the user query. 

Consider an example where the reference source contains “London is the capital of UK.
 Tokyo is the capital of Japan” and the user query is “What is the capital of Japan?”. A
 response such as “The capital of Japan is London” will be considered ungrounded and
 factually incorrect, where as a response such as “The capital of UK is London” will be
 considered irrelevant, even if it’s correct and grounded in the source. 

Note 

When a request includes multiple grounding_source tags, the guardrail
 combines and evaluates all the provided grounding_source values
 together, rather than considering each grounding_source separately.
 This behavior is identical for the query tag. 

Note 

Contextual grounding policy currently supports a maximum of 100,000 characters for
 grounding source, 1,000 characters for query, and 5,000 characters for
 response. 

Confidence scores and thresholds 

Contextual grounding checks generate confidence scores corresponding to grounding and
 relevance for each model response processed based on the source and user query provided.
 You can configure thresholds to filter model responses based on the generated scores.
 The filtering threshold determines the minimum allowable confidence score for the model
 response to be considered as grounded and relevant in your generative AI application.
 For example, if your grounding threshold and relevance threshold are each set at 0.7,
 all model responses with a grounding or relevance score of less than 0.7 will be
 detected as hallucinations and blocked in your application. As the filtering threshold
 is increased, the likelihood of blocking un-grounded and irrelevant content increases,
 and the probability of seeing hallucinated content in your application decreases. You
 can configure threshold values of grounding and relevance between 0 and 0.99. A
 threshold of 1 is invalid as that will block all content. 

Contextual grounding checks require 3 components to perform the check: the grounding
 source, the query, and the content to guard (or the model response). These are
 configured differently depending on whether you are using Invoke APIs,
 Converse APIs, or ApplyGuardrail directly. 

Grounding source – contextual information needed to answer any user
 queries. For example, “London is the capital of UK. Tokyo is the capital of
 Japan”. 

Query – a question a user may ask. For example, “What is the capital of
 Japan?”. 

Content to guard – the text that should be guarded relative to the
 grounding source and query. For Invoke and Converse APIs, this is
 the model response. For example, this can be “The capital of Japan is
 Tokyo”. 

Ungrounded example 

Grounding source - “London is the capital of UK. Tokyo is the capital of
 Japan.” 

Query - “What is the capital of Japan?” 

Content to guard - “The capital of Japan is London.” 

In this example, the content to guard is relevant to the query but is ungrounded as it
 does not use the grounding source correctly. This would have a low grounding
 score. 

Irrelevant example 

Grounding source - “London is the capital of UK. Tokyo is the capital of
 Japan.” 

Query - “What is the capital of Japan?” 

Content to guard - “The capital of UK is London.” 

In this example, the content to guard is grounded but not relevant. It uses
 information from the grounding source but does not answer the query. This would have a
 low relevance score. 

Ungrounded and irrelevant example 

Grounding source - “London is the capital of UK. Tokyo is the capital of
 Japan.” 

Query - “What is the capital of Japan?” 

Content to guard - “It is raining outside.” 

In this example, the content to guard is not grounded and not relevant. It neither
 uses information from the grounding source nor does it answer the query. This would have
 a low grounding and relevance score. 

More Examples 

Consider a banking application that is designed to answer questions associated with
 fees and charges. 

Source: 

There are no fees associated with opening a checking account. 

The monthly fee for maintaining a checking account is $10. 

There is a 1% transaction charge for international transfers. 

There are no charges associated with domestic transfers. 

The charges associated with late payments of credit card bill is
 23.99%. 

Based on the above source, there can be four scenarios depending on the user’s
 query. 

Grounded and Relevant 

Q: What are the fees associated with checking account? 

A: The monthly fee for maintaining a checking account is $10. There are no
 charges associated with domestic transfers. However, there is a 1% transaction
 charge for international transfers. There are no fees associated with opening a
 checking account. 

Un-grounded but Relevant 

Q: What is the transaction charge associated with credit card. 

A: The transaction charges associated with the credit card is 23.99%. 

Grounded but Irrelevant 

Q: What are the charges for using a checking bank account? 

A: Based on the information provided, the late payment fee for a credit card
 is 23.99%. 

Un-grounded and Irrelevant 

Q: What are the charges for using a checking bank account? 

A: The charges for the brokerage account are $0.5 per trading
 transaction. 

Topics 

Add contextual grounding
 checks with the console 

Calling contextual
 grounding check with Invoke APIs 

Calling contextual
 grounding check with Converse APIs 

Calling
 contextual grounding check with ApplyGuardrail API 

Add contextual grounding
 checks with the console 

Sign in to the AWS Management Console with an IAM identity that has permissions to use the Amazon Bedrock console. Then, open the Amazon Bedrock console at https://console.aws.amazon.com/bedrock . 

From the left navigation pane, choose Guardrails , and
 then choose Create guardrail . 

For Provide guardrail details page, do the
 following: 

In the Guardrail details section, provide a Name and optional Description for the guardrail. 

For Messaging for blocked prompts , enter a
 message that displays when your guardrail is applied. Select the Apply the same blocked message for
 responses checkbox to use the same message when your
 guardrail is applied on the response. 

(Optional) To enable cross-Region inference for your guardrail, expand Cross-Region inference , and then select Enable cross-Region inference for your
 guardrail . Choose a guardrail profile that defines
 the destination AWS Regions where guardrail inference requests can
 be routed. 

(Optional) By default, your guardrail is encrypted with an
 AWS managed key. To use your own customer-managed KMS key,
 expand KMS key selection and select the Customize encryption settings (advanced) checkbox. 

You can select an existing AWS KMS key or select Create an
 AWS KMS key to create a new one. 

(Optional) To add tags to your guardrail, expand Tags , and then, select Add new
 tag for each tag you define. 

For more information, see Tagging Amazon Bedrock resources . 

Choose Next . 

On the Add contextual grounding check page, configure
 thresholds to block un-grounded or irrelevant information. 

Note 

For each type of check, you can move the slider or input a threshold
 value from 0 to 0.99. Select an appropriate threshold for your uses. A
 higher threshold requires responses to be grounded or relevant with a
 high degree of confidence to be allowed. Responses below the threshold
 will be filtered. 

In the Grounding field, select Enable grounding check to check if model
 responses are grounded. 

In the Relevance field, select Enable relevance check to check if model
 responses are relevant. 

When you finish configuring sensitive information filters, select Next or Skip to review and
 create . 

Calling contextual
 grounding check with Invoke APIs 
To mark the grounding source and query within the input, we provide 2 tags that
 work the same way as input tags. These tags are amazon-bedrock-guardrails-groundingSource_xyz and amazon-bedrock-guardrails-query_xyz assuming the tag suffix is xyz.
 For example: 

{ "text": """
<amazon-bedrock-guardrails-groundingSource_xyz>London is the capital of UK. Tokyo is the capital of Japan. </amazon-bedrock-guardrails-groundingSource_xyz>

<amazon-bedrock-guardrails-query_xyz>What is the capital of Japan?</amazon-bedrock-guardrails-query_xyz>
""",
 "amazon-bedrock-guardrailConfig": { "tagSuffix": "xyz",
 },
} 
Note that the model response is required to perform the contextual grounding
 checks and so the checks will only be performed on output and not on the
 prompt. 

These tags can be used alongside the guardContent tags. If no guardContent tags
 are used, then the guardrail will default to applying all the configured policies on
 the entire input, including the grounding source and query. If the guardContent tags
 are used, then the contextual grounding check policy will investigate just the
 grounding source, query, and response, while the remaining policies will investigate
 the content within the guardContent tags. 

Calling contextual
 grounding check with Converse APIs 
To mark the grounding source and query for Converse APIs, use the
 qualifiers field in each guard content block. For example: 

[ { "role": "user",
 "content": [ { "guardContent": { "text": { "text": "London is the capital of UK. Tokyo is the capital of Japan",
 "qualifiers": ["grounding_source"],
 }
 }
 }, { "guardContent": { "text": { "text": "What is the capital of Japan?",
 "qualifiers": ["query"],
 }
 }
 },
 ],
 }
] 
Note that the model response is required to perform the contextual grounding
 checks and so the checks will only be performed on output and not on the
 prompt. 

If none of the content blocks are marked with the guard_content qualifier, then
 the contextual grounding checks policy will investigate just the grounding source,
 query, and response. The remaining policies will follow the default investigation
 behavior: system prompt defaults to not getting investigated and messages defaults
 to getting investigated. If, however, a content block is marked with the
 guard_content qualifier, then the contextual grounding checks policy will
 investigate just the grounding source, query, and response, while the remaining
 policies will investigate the content marked with the guardContent tags. 

Calling
 contextual grounding check with ApplyGuardrail API 
Using contextual grounding check with ApplyGuardrail is similar to
 using it with the Converse APIs. To mark the grounding source and
 query for ApplyGuardrail , use the qualifiers field in each content
 block. However, because a model is not invoked with ApplyGuardrail , you
 must also provide an extra content block with the content to be guarded. This
 content block can be optionally qualified with guard_content and is equivalent to
 the model response in the Invoke* or Converse* APIs. For example: 

[ { "text": { "text": "London is the capital of UK. Tokyo is the capital of Japan",
 "qualifiers": [
 "grounding_source"
 ]
 }
 }, { "text": { "text": "What is the capital of Japan?",
 "qualifiers": [
 "query"
 ]
 }
 }, { "text": { "text": "The capital of Japan is Tokyo."
 }
 }
] 
Note that the model response is required to perform the contextual grounding
 checks and so the checks will only be performed on output and not on the
 prompt. 

If none of the content blocks are marked with the guard_content qualifier, then
 the contextual grounding checks policy will investigate just the grounding source,
 query, and response. The remaining policies will follow the default investigation
 behavior: system prompt defaults to not getting investigated and messages defaults
 to getting investigated. If, however, a content block is marked with the
 guard_content qualifier, then the contextual grounding checks policy will
 investigate just the grounding source, query, and response, while the remaining
 policies will investigate the content marked with the guardContent tags. 

Document Conventions 
Add sensitive information
 filters 
Options for handling harmful content 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
