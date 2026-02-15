# Detect and filter harmful content by using Amazon Bedrock Guardrails - Amazon Bedrock Detect and filter harmful content by using Amazon Bedrock Guardrails - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Detect and filter harmful content by using Amazon Bedrock Guardrails - Amazon Bedrock 
Detect and filter harmful content by using Amazon Bedrock Guardrails - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Detect and filter harmful content by using Amazon Bedrock Guardrails 

Amazon Bedrock Guardrails provides configurable safeguards to help you build safe generative AI applications. With comprehensive safety and privacy controls across
 foundation models (FMs), Amazon Bedrock Guardrails offers a consistent user experience to help detect and filter undesirable content and protect sensitive information that might be present in
 user inputs or model responses (excluding reasoning content blocks). 

You can use Amazon Bedrock Guardrails across multiple use cases and applications. Below are a few examples: 

A chatbot application to help filter harmful user inputs and
 toxic model responses. 

A banking application to help block user queries or model
 responses associated with seeking or providing illegal investment advice. 

A call center application to summarize conversation transcripts between users and
 agents can use guardrails to redact users’ personally identifiable information (PII)
 to protect user privacy. 

Amazon Bedrock Guardrails provides the following safeguards (also known as filters) to detect and filter
 undesirable content: 

Content filters – This filter helps you detect and filter harmful
 text or image content in input prompts or model responses. Filtering is done based
 on detection of certain predefined harmful content categories: Hate, Insults,
 Sexual, Violence, Misconduct and Prompt Attack. You can configure the filter
 strength for each of these categories based on your use cases. These categories are supported for both Classic
 and Standard tiers . With Standard tier,
 detection of undesirable content is extended to protection against harmful content
 introduced within code elements including comments, variable and function names, and
 string literals. 

Denied topics – You can define a set of topics that
 are undesirable in the context of your application. The filter will help block them
 if detected in user queries or model responses. With Standard tier , detection of undesirable content
 is extended to protection against harmful content introduced within code elements
 including comments, variables and function names, and string literals. 

Word filters – You can define a set of custom words or phrases (exact match)
 that you want to block in the interaction between end users and generative AI applications. For example, you can block 
 profanity (use a ready-to-use option) as well as custom words such as competitor names. 

Sensitive information filters – You can configure
 this filter to help block or mask sensitive information, such as personally identifiable
 information (PII), in user inputs and model responses. Blocking or
 masking is done based on probabilistic detection of sensitive information in
 in entities such as SSN number, Date of Birth, address, etc. This filter
 also allows configuring regular expression based detection of patterns (custom regex). 

Contextual grounding checks – This filter helps you detect
 hallucinations in model responses if they are not grounded (factually inaccurate or add new information) in the source or are irrelevant to 
 to the user's query. For example, you can block or flag responses in retrieval-augmented generation (RAG) applications. If the model responses deviate
 from the information in the retrieved source or doesn't answer the question from the user. 

Automated Reasoning checks – This filter helps you 
 validate the accuracy of foundation model responses against a set of logical rules.
 You can use Automated Reasoning checks to detect hallucinations, suggest
 corrections, and highlight unstated assumptions in model responses. 

In addition to the above filters, you can also configure the messages to be returned to
 the user if a user input or model response is in violation of the filters defined in the
 guardrail. 

Experiment and benchmark with different configurations and use the built-in test window to
 ensure that the results meet your use-case requirements. When you create a guardrail, a
 working draft is automatically available for you to iteratively modify. Experiment with
 different configurations and use the built-in test window to see whether they are
 appropriate for your use-case. If you are satisfied with a set of configurations, you can
 create a version of the guardrail and use it with supported foundation models. 

Guardrails can be used directly with FMs during the inference API invocation by specifying
 the guardrail ID and the version. Guardrails can also be used directly through the ApplyGuardrail API without invoking the foundation models. If a guardrail
 is used, it will evaluate the input prompts and the FM completions against the defined
 filters. 

For retrieval augmented generation (RAG) or conversational applications, you might need to
 evaluate only user input prompts while discarding system instructions,
 search results, conversation history, or a few short examples. To selectively evaluate a
 section of the input prompt, see Apply tags to user input to filter content The ability to evaluate only a section of the input prompt is available
 through the AWS SDK and not available on the management console including the Bedrock Playground and the Bedrock Guardrails management console. 

Topics 

How Amazon Bedrock Guardrails works 

Supported Regions and models for Amazon Bedrock Guardrails 

Safeguard tiers for guardrails policies 

Languages supported by Amazon Bedrock Guardrails 

Prerequisites for using Amazon Bedrock Guardrails 

Set up permissions to use Amazon Bedrock Guardrails 

Create your guardrail 

Distribute guardrail inference across AWS Regions 

Apply cross-account safeguards with Amazon Bedrock Guardrails enforcements 

Test your guardrail 

View information about your guardrails 

Modify your guardrail 

Delete your guardrail 

Deploy your guardrail 

Use cases for Amazon Bedrock Guardrails 

Document Conventions 
Prompt injection security 
Overview 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
