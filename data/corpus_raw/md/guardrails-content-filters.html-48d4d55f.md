# Block harmful words and conversations with content filters - Amazon Bedrock Block harmful words and conversations with content filters - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-content-filters.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Block harmful words and conversations with content filters - Amazon Bedrock 
Block harmful words and conversations with content filters - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
Configure content filters
 for your guardrail 

Block harmful words and conversations
 with content filters 

Amazon Bedrock Guardrails supports content filters to help detect and filter harmful user inputs and
 model-generated outputs in natural language as well as code-related content in
 Standard tier. Content filters are supported across the following categories: 

Hate 

Describes input prompts and model responses that discriminate, criticize,
 insult, denounce, or dehumanize a person or group on the basis of an
 identity (such as race, ethnicity, gender, religion, sexual orientation,
 ability, and national origin). 

Insults 

Describes input prompts and model responses that includes demeaning,
 humiliating, mocking, insulting, or belittling language. This type of
 language is also labeled as bullying. 

Sexual 

Describes input prompts and model responses that indicates sexual
 interest, activity, or arousal using direct or indirect references to body
 parts, physical traits, or sex. 

Violence 

Describes input prompts and model responses that includes glorification
 of, or threats to inflict physical pain, hurt, or injury toward a person,
 group, or thing. 

Misconduct 

Describes input prompts and model responses that seeks or provides
 information about engaging in criminal activity, or harming, defrauding, or
 taking advantage of a person, group or institution. 

Configure content filters
 for your guardrail 
You can configure content filters for your guardrail by using the AWS Management Console or
 Amazon Bedrock API. 
Console 

Sign in to the AWS Management Console with an IAM identity that has permissions to use the Amazon Bedrock console. Then, open the Amazon Bedrock console at https://console.aws.amazon.com/bedrock . 

From the left navigation pane, choose Guardrails , and then choose Create guardrail . 

For Provide guardrail details page,
 do the following: 

In the Guardrail details section, provide a Name and
 optional Description for the
 guardrail. 

For Messaging for blocked
 prompts , enter a message that displays
 when your guardrail is applied. Select the Apply the same blocked message for
 responses checkbox to use the same
 message when your guardrail is applied on the
 response. 

(Optional) To enable cross-Region
 inference for your guardrail, expand Cross-Region inference , and
 then select Enable cross-Region inference
 for your guardrail . Choose a guardrail
 profile that defines the destination AWS Regions
 where guardrail inference requests can be
 routed. 

(Optional) By default, your guardrail is encrypted
 with an AWS managed key. To use your own
 customer-managed KMS key, expand KMS key selection and
 select the Customize encryption settings
 (advanced) checkbox. 

You can select an existing AWS KMS key or select Create an AWS KMS key to create
 a new one. 

(Optional) To add tags to your guardrail, expand Tags . Then select Add new tag for each tag that
 you define. 

For more information, see Tagging Amazon Bedrock resources . 

Choose Next . 

On the Configure content filters page, set up how strongly you want to filter out content
 related to the categories defined in Block harmful words and conversations
 with content filters by doing
 the following: 

Select Configure harmful categories
 filter . Select Text and/or Image to filter text or image
 content from prompts or responses to the model.
 Select None, Low, Medium, or
 High for the level of filtration you
 want to apply to each category. You can choose to
 have different filter levels for prompts or
 responses. You can select the filter for prompt
 attacks in the harmful categories. Configure how
 strict you want each filter to be for prompts that
 the user provides to the model. 

Choose Block or Detect (no action) to
 determine what action your guardrail takes when it
 detects harmful content in prompts and
 responses. 

For more information, see Options for handling
 harmful content detected by Amazon Bedrock Guardrails . 

For Set threshold , select None, Low, Medium, or High for the level of filtration you want to apply to
 each category. 

You can choose to have different filter levels for
 prompts and responses. 

For Content filters tier ,
 choose the safeguard tier that you want your
 guardrail to use for filtering text-based prompts
 and responses. For more information, see Safeguard tiers for guardrails policies . 

Choose Next to configure
 other policies as needed or Skip to Review
 and create to finish creating your
 guardrail. 

Review the settings for your guardrail. 

Select Edit in any section
 you want to make changes to. 

When you're done configuring policies, select Create to create the
 guardrail. 

API 
Configure content filters for your guardrail by sending a CreateGuardrail request. The request format is as
 follows: 

POST /guardrails HTTP/1.1
Content-type: application/json { "blockedInputMessaging": "string",
 "blockedOutputsMessaging": "string",
 "contentPolicyConfig": { "filtersConfig": [ { "inputAction": "BLOCK | NONE",
 "inputModalities": [ "TEXT" ], 
 "inputStrength": "NONE | LOW | MEDIUM | HIGH",
 "outputStrength": "NONE | LOW | MEDIUM | HIGH",
 "type": "SEXUAL | VIOLENCE | HATE | INSULTS | MISCONDUCT"
 }
 ],
 "tierConfig": { "tierName": "CLASSIC | STANDARD"
 }
 },
 "crossRegionConfig": { "guardrailProfileIdentifier": "string"
 },
 "description": "string",
 "name": "string"
} 

Specify a name and description for the guardrail. 

Specify messages for when the guardrail successfully
 blocks a prompt or a model response in the blockedInputMessaging and blockedOutputsMessaging fields. 

Specify filter strengths for the harmful categories
 available the contentPolicyConfig object. 

Each item in the filtersConfig list pertains
 to a harmful category. For more information, see Block harmful words and conversations
 with content filters . For more
 information about the fields in a content filter, see ContentFilter . 

(Optional) For inputAction and outputAction , specify the action your
 guardrail takes when it detects harmful content in
 prompts and responses. 

(Optional) Specify the action to take when harmful
 content is detected in prompts using inputAction or responses using outputAction . Choose BLOCK to block content and replace
 with blocked messaging, or NONE to take
 no action but return detection information. For more
 information, see Options for handling
 harmful content detected by Amazon Bedrock Guardrails . 

Specify the strength of the filter for prompts in
 the inputStrength field and for model
 responses in the outputStrength field. 

Specify the category in the type field. 

(Optional) Specify a safeguard tier for your guardrail in
 the tierConfig object within the contentPolicyConfig object. Options include STANDARD and CLASSIC tiers. 

For more information, see Safeguard tiers for guardrails policies . 

(Optional) To enable cross-Region
 inference , specify a guardrail profile in the crossRegionConfig object. This is required
 when using the STANDARD tier. 

The response format looks like this: 

HTTP/1.1 202
Content-type: application/json { "createdAt": "string",
 "guardrailArn": "string",
 "guardrailId": "string",
 "version": "string"
} 

Document Conventions 
Configure content filters 
Content filters (images) 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
