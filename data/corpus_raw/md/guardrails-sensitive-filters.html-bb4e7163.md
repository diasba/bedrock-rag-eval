# Remove PII from conversations by using sensitive information filters - Amazon Bedrock Remove PII from conversations by using sensitive information filters - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Remove PII from conversations by using sensitive information filters - Amazon Bedrock 
Remove PII from conversations by using sensitive information filters - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
Configure
 sensitive information policy for your guardrail 

Remove PII from conversations by using
 sensitive information filters 

Amazon Bedrock Guardrails helps detect sensitive information, such as personally identifiable information
 (PII), in input prompts or model responses using sensitive information filters. This filter is a probabilistic machine learning (ML) based solution that is context-dependent
 and detects sensitive information based on the context within input prompts or model responses. You can configure by selecting from a set of built-in PIIs offered by Amazon Bedrock Guardrails specific to your use case
 or organization by defining it along with regular expressions (custom regex) that work based on pattern matching to block or mask PII data. 

Sensitive information detection works across both natural language and code domains,
 including code syntax, comments, string literals, and hybrid content. This helps
 identify PII embedded in code elements such as variable names, hardcoded credentials, or
 code documentation. 

You can configure the following modes for handling sensitive information that
 guardrails detects: 

Block — Sensitive information filter
 policies can block requests or responses that include sensitive information.
 Examples of such applications might include general questions and answers
 based on public documents. If sensitive information is detected in
 the prompt or response, the guardrail blocks all the content and returns a
 message that you configure. 

Mask — Sensitive information filter
 policies can anonymize or redact information from model requests or responses.
 For example, guardrails mask PIIs while generating summaries of conversations
 between users and customer service agents. If sensitive information is detected
 in the model request or response, the guardrail masks it and replaces it with
 the PII type (for example, { NAME} or { EMAIL} ). 

Amazon Bedrock Guardrails offers the following PIIs to block or anonymize: 

General 

ADDRESS 

A physical address, such as "100 Main Street, Anytown, USA" or "Suite
 #12, Building 123". An address can include information such as the
 street, building, location, city, state, country, county, zip code,
 precinct, and neighborhood. 

AGE 

An individual's age, including the quantity and unit of time. For
 example, in the phrase "I am 40 years old," Amazon Bedrock Guardrails recognizes "40 years"
 as an age. 

NAME 

An individual's name. This entity type does not include titles, such
 as Dr., Mr., Mrs., or Miss. Amazon Bedrock Guardrails does not apply this entity type to
 names that are part of organizations or addresses. For example,
 guardrails recognizes the "John Doe Organization" as an organization,
 and it recognizes "Jane Doe Street" as an address. 

EMAIL 

An email address, such as marymajor@email.com . 

PHONE 

A phone number. This entity type also includes fax and pager numbers. 

USERNAME 

A user name that identifies an account, such as a login name, screen
 name, nick name, or handle. 

PASSWORD 

An alphanumeric string that is used as a password, such as
 "* very20special#pass* ". 

DRIVER_ID 

The number assigned to a driver's license, which is an official
 document permitting an individual to operate one or more motorized
 vehicles on a public road. A driver's license number consists of
 alphanumeric characters. 

LICENSE_PLATE 

A license plate for a vehicle is issued by the state or country where
 the vehicle is registered. The format for passenger vehicles is
 typically five to eight digits, consisting of upper-case letters and
 numbers. The format varies depending on the location of the issuing
 state or country. 

VEHICLE_IDENTIFICATION_NUMBER 

A Vehicle Identification Number (VIN) uniquely identifies a vehicle.
 VIN content and format are defined in the ISO 3779 specification. Each country has specific codes and formats for VINs. 

Finance 

CREDIT_DEBIT_CARD_CVV 

A three-digit card verification code (CVV) that is present on VISA,
 MasterCard, and Discover credit and debit cards. For American Express
 credit or debit cards, the CVV is a four-digit numeric code. 

CREDIT_DEBIT_CARD_EXPIRY 

The expiration date for a credit or debit card. This number is usually
 four digits long and is often formatted as month/year or MM/YY . Amazon Bedrock Guardrails
 recognizes expiration dates such as 01/21 , 01/2021 , and Jan 2021 . 

CREDIT_DEBIT_CARD_NUMBER 

The number for a credit or debit card. These numbers can vary from 13
 to 16 digits in length. However, Amazon Bedrock also recognizes credit or
 debit card numbers when only the last four digits are present. 

PIN 

A four-digit personal identification number (PIN) with which you can
 access your bank account. 

INTERNATIONAL_BANK_ACCOUNT_NUMBER 

An International Bank Account Number has specific formats in each
 country. For more information, see www.iban.com/structure . 

SWIFT_CODE 

A SWIFT code is a standard format of Bank Identifier Code (BIC) used
 to specify a particular bank or branch. Banks use these codes for money
 transfers such as international wire transfers. 

SWIFT codes consist of eight or 11 characters. The 11-digit codes
 refer to specific branches, while eight-digit codes (or 11-digit codes
 ending in 'XXX') refer to the head or primary office. 

IT 

IP_ADDRESS 

An IPv4 address, such as 198.51.100.0 . 

MAC_ADDRESS 

A media access control (MAC) address is a unique
 identifier assigned to a network interface controller (NIC). 

URL 

A web address, such as www.example.com . 

AWS_ACCESS_KEY 

A unique identifier that's associated with a secret access key; you
 use the access key ID and secret access key to sign programmatic AWS
 requests cryptographically. 

AWS_SECRET_KEY 

A unique identifier that's associated with an access key. You use the
 access key ID and secret access key to sign programmatic AWS requests
 cryptographically. 

USA specific 

US_BANK_ACCOUNT_NUMBER 

A US bank account number, which is typically 10 to 12 digits long. 

US_BANK_ROUTING_NUMBER 

A US bank account routing number. These are typically nine digits
 long, 

US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER 

A US Individual Taxpayer Identification Number (ITIN) is a nine-digit
 number that starts with a "9" and contain a "7" or "8" as the fourth
 digit. An ITIN can be formatted with a space or a dash after the third
 and forth digits. 

US_PASSPORT_NUMBER 

A US passport number. Passport numbers range from six to nine
 alphanumeric characters. 

US_SOCIAL_SECURITY_NUMBER 

A US Social Security Number (SSN) is a nine-digit number that is
 issued to US citizens, permanent residents, and temporary working
 residents. 

Canada specific 

CA_HEALTH_NUMBER 

A Canadian Health Service Number is a 10-digit unique identifier,
 required for individuals to access healthcare benefits. 

CA_SOCIAL_INSURANCE_NUMBER 

A Canadian Social Insurance Number (SIN) is a nine-digit unique
 identifier, required for individuals to access government programs and
 benefits. 

The SIN is formatted as three groups of three digits, such as 123-456-789 . A SIN can be validated through a
 simple check-digit process called the Luhn
 algorithm . 

UK Specific 

UK_NATIONAL_HEALTH_SERVICE_NUMBER 

A UK National Health Service Number is a 10-17 digit number, such as 485 777 3456 . The current system formats the
 10-digit number with spaces after the third and sixth digits. The final
 digit is an error-detecting checksum. 

UK_NATIONAL_INSURANCE_NUMBER 

A UK National Insurance Number (NINO) provides individuals with access
 to National Insurance (social security) benefits. It is also used for
 some purposes in the UK tax system. 

The number is nine digits long and starts with two letters, followed
 by six numbers and one letter. A NINO can be formatted with a space or a
 dash after the two letters and after the second, forth, and sixth
 digits. 

UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER 

A UK Unique Taxpayer Reference (UTR) is a 10-digit number that
 identifies a taxpayer or a business. 

Custom 

Regex filter 

You can use regular expressions to define patterns for a guardrail
 to recognize and act upon such as serial number, booking ID, or other custom patterns. 

Note 

The PII model performs more effectively when it is provided with sufficient
 context. To enhance its accuracy, include more contextual information and avoid
 submitting single words or short phrases to the model. Since PII can be
 context-dependent (for example. a string of digits might represent an AWS KMS key
 or a user ID depending on the surrounding information), providing comprehensive
 context is crucial for accurate identification. 

Note 

A custom regex filter of sensitive information filters does not support a regex
 lookaround match. 

Configure
 sensitive information policy for your guardrail 
You can configure sensitive information policies for your guardrail by using the
 AWS Management Console or Amazon Bedrock API. 
Console 

Sign in to the AWS Management Console with an IAM identity that has permissions to use the Amazon Bedrock console. Then, open the Amazon Bedrock console at https://console.aws.amazon.com/bedrock . 

From the left navigation pane, choose Guardrails , and then choose Create guardrail . 

For Provide guardrail details page, do
 the following: 

In the Guardrail details section,
 provide a Name and optional Description for the
 guardrail. 

For Messaging for blocked
 prompts , enter a message that displays when
 your guardrail is applied. Select the Apply
 the same blocked message for responses checkbox to use the same message when your guardrail is
 applied on the response. 

(Optional) To enable cross-Region
 inference for your guardrail, expand Cross-Region inference , and
 then select Enable cross-Region inference for
 your guardrail . Choose a guardrail
 profile that defines the destination AWS Regions where
 guardrail inference requests can be routed. 

(Optional) By default, your guardrail is encrypted
 with an AWS managed key. To use your own
 customer-managed KMS key, expand KMS key
 selection and select the Customize encryption settings
 (advanced) checkbox. 

You can select an existing AWS KMS key or select Create an AWS KMS key to create a
 new one. 

(Optional) To add tags to your guardrail, expand Tags , and then, select Add new tag for each tag you
 define. 

For more information, see Tagging Amazon Bedrock resources . 

Choose Next . 

On the Add sensitive information filters
 page page, do the following to configure filters
 to block or mask sensitive information: 

In the PII types section,
 configure the personally identifiable information (PII)
 categories to block, mask, or take no action (detect
 mode). You have the following options: 

To add all PII types, select the dropdown
 arrow next to Add PII type .
 Then select the guardrail behavior to apply to
 them. 

Warning 

If you specify a behavior, any existing
 behavior that you configured for PII types will be
 overwritten. 

To delete a PII type, select the trash can
 icon ( ). 

To delete rows that contain errors, select Delete all and then select Delete all rows with
 error 

To delete all PII types, select Delete all and then select Delete all rows 

To search for a row, enter an expression in
 the search bar. 

To show only rows with errors, select the
 dropdown menu labeled Show
 all and select Show errors
 only . 

To configure the size of each page in the
 table or the column display in the table, select
 the settings icon ( ). Set your
 preferences and then select Confirm . 

In the Regex patterns section,
 use regular expressions to define patterns for the
 guardrail to filter. You have the following
 options: 

To add a pattern, select Add regex
 pattern . Configure the following
 fields: 

Field Description 
Name A name for the pattern 
Regex pattern A regular expression that defines the
 pattern 
Input Choose whether to Block content containing the
 pattern or Mask it with an
 identifier. To take no action, select Detect (no action) . 
Output 
Add description (Optional) Write a description for the
 pattern 

To edit a pattern, select the three dots icon
 in the same row as the topic in the Actions column. Then select Edit . After you are finished
 editing, select Confirm . 

To delete a pattern or patterns, select the
 checkboxes for the patterns to delete. Select Delete and then select Delete selected . 

To delete all the patterns, select Delete and then select Delete all . 

To search for a pattern, enter an expression
 in the search bar. 

To configure the size of each page in the
 table or the column display in the table, select
 the settings icon ( ). Set your
 preferences and then select Confirm . 

When you finish configuring sensitive information
 filters, select Next or Skip to review and
 create . 

API 
To create a guardrail with sensitive information policies, send a CreateGuardrail request. The request format is as follows: 

POST /guardrails HTTP/1.1
Content-type: application/json { "blockedInputMessaging": "string",
 "blockedOutputsMessaging": "string",
 "sensitiveInformationPolicyConfig": { "piiEntitiesConfig": [ { "type": "ADDRESS | EMAIL | PHONE | NAME | SSN | ...",
 "action": "BLOCK | ANONYMIZE | NONE",
 "inputAction": "BLOCK | ANONYMIZE | NONE",
 "inputEnabled": true,
 "outputAction": "BLOCK | ANONYMIZE | NONE",
 "outputEnabled": true
 }],
 "regexesConfig": [ { "name": "string",
 "pattern": "string",
 "action": "BLOCK | ANONYMIZE | NONE",
 "description": "string",
 "inputAction": "BLOCK | ANONYMIZE | NONE",
 "inputEnabled": true,
 "outputAction": "BLOCK | ANONYMIZE | NONE",
 "outputEnabled": true
 }]
 },
 "description": "string",
 "kmsKeyId": "string",
 "name": "string",
 "tags": [ { "key": "string",
 "value": "string"
 }],
 "crossRegionConfig": { "guardrailProfileIdentifier": "string"
 }
} 

Specify a name and description for
 the guardrail. 

Specify messages for when the guardrail successfully blocks a
 prompt or a model response in the blockedInputMessaging and blockedOutputsMessaging fields. 

Configure sensitive information policies in the sensitiveInformationPolicyConfig object: 

Use piiEntitiesConfig array to configure
 predefined PII entity types: 

Specify the PII entity type in the type field. Valid values include ADDRESS , EMAIL , PHONE , NAME , US_SOCIAL_SECURITY_NUMBER , among
 others. 

Specify the action to take when the PII entity
 is detected in the action field.
 Choose BLOCK to block content, ANONYMIZE to mask the content, or NONE to take no action but return
 detection information. 

(Optional) Use inputAction , inputEnabled , outputAction , and outputEnabled to configure different
 behaviors for prompts and responses. 

Use regexesConfig array to define custom
 patterns to detect: 

Specify a name for the regex
 pattern (1-100 characters). 

Define the regular expression pattern to detect (1-500
 characters). 

Specify the action to take when
 the pattern is detected. Choose BLOCK to block content, ANONYMIZE to mask
 the content, or NONE to take no
 action but return detection information. 

(Optional) Provide a description for the regex pattern (1-1000 characters). 

(Optional) Use inputAction , inputEnabled , outputAction , and outputEnabled to configure different
 behaviors for prompts and responses. 

(Optional) Attach any tags to the guardrail. For more
 information, see Tagging Amazon Bedrock resources . 

(Optional) For security, include the ARN of a KMS key in the kmsKeyId field. 

(Optional) To enable cross-Region inference , specify a guardrail profile
 in the crossRegionConfig object. 

The response format is as follows: 

HTTP/1.1 202
Content-type: application/json { "createdAt": "string",
 "guardrailArn": "string",
 "guardrailId": "string",
 "version": "string"
} 

Document Conventions 
Add word filters 
Add contextual
 grounding checks 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
