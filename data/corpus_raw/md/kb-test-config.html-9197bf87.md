# Configure and customize queries and response generation - Amazon Bedrock Configure and customize queries and response generation - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Configure and customize queries and response generation - Amazon Bedrock 
Configure and customize queries and response generation - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Configure and customize queries and response
 generation 

You can configure and customize retrieval and response generation, further improving the
 relevancy of responses. For example, you can apply filters to document metadata
 fields/attributes to use the most recently updated documents or documents with recent
 modification times. 

Note 

All of the following configurations, except for Orchestration and
 generation , are only applicable to unstructured data sources. 

To learn more about these configurations in the console or the API, select from the
 following topics: 

When you query a knowledge base, Amazon Bedrock returns up to five results in the response
 by default. Each result corresponds to a source chunk. 

Note 

The actual number of results in the response might be less than the specified numberOfResults value, since this parameter sets the maximum number of results to return. If you have configured hierarchical chunking for your chunking strategy, the numberOfResults parameter maps to the number of child chunks that the knowledge base will retrieve. Since child chunks that share the same parent chunk are replaced with the parent chunk in the final response, the number of results returned might be less than the requested amount. 

To modify the maximum number of results to return, choose the tab for your preferred method, and then follow the steps: 
Console 
Follow the console steps at Query a knowledge base and retrieve data or Query a knowledge base and generate responses based off the retrieved data . In the Configurations pane,
 expand the Source chunks section and enter the
 maximum number of source chunks to return. 
API 
When you make a Retrieve or RetrieveAndGenerate request, include a retrievalConfiguration field, mapped to a KnowledgeBaseRetrievalConfiguration object. To see the location of this field, refer to the Retrieve and RetrieveAndGenerate request bodies in the API reference. 

The following JSON object shows the minimal fields required in the KnowledgeBaseRetrievalConfiguration object to set the maximum number of results to
 return: 

"retrievalConfiguration": { "vectorSearchConfiguration": { "numberOfResults": number
 }
} 
Specify the maximum number of retrieved results (see the numberOfResults field in KnowledgeBaseRetrievalConfiguration for the
 range of accepted values) to return in the numberOfResults field. 

The search type defines how data sources in the knowledge base are queried. The
 following search types are possible: 

Note 

Hybrid search is only supported for Amazon RDS, Amazon OpenSearch Serverless, and MongoDB vector stores that contain
 a filterable text field. If you use a different vector store or your vector store doesn't 
 contain a filterable text field, the query uses semantic search. 

Default – Amazon Bedrock decides the search
 strategy for you. 

Hybrid – Combines searching vector
 embeddings (semantic search) with searching through the raw text. 

Semantic – Only searches vector
 embeddings. 

To learn how to define the search type, choose the tab for your preferred method, and then follow the steps: 
Console 
Follow the console steps at Query a knowledge base and retrieve data or Query a knowledge base and generate responses based off the retrieved data . When you open the Configurations pane, expand the Search type section, turn on Override
 default search , and select an option. 
API 
When you make a Retrieve or RetrieveAndGenerate request, include a retrievalConfiguration field, mapped to a KnowledgeBaseRetrievalConfiguration object. To see the location of this field, refer to the Retrieve and RetrieveAndGenerate request bodies in the API reference. 

The following JSON object shows the minimal fields required in the KnowledgeBaseRetrievalConfiguration object to set search type configurations: 

"retrievalConfiguration": { "vectorSearchConfiguration": { "overrideSearchType": "HYBRID | SEMANTIC"
 }
} 
Specify the search type in the overrideSearchType field.
 You have the following options: 

If you don't specify a value, Amazon Bedrock decides which search
 strategy is best suited for your vector store
 configuration. 

HYBRID – Amazon Bedrock queries the knowledge
 base using both the vector embeddings and the raw text. 

SEMANTIC – Amazon Bedrock queries the
 knowledge base using its vector embeddings. 

Console 
Follow the console steps at Query a knowledge base and generate responses based off the retrieved data . When you open the Configurations pane, expand the Streaming preference section and turn on Stream response . 
API 
To stream responses, use the RetrieveAndGenerateStream API. For more
 details about filling out the fields, see the API tab at Query a knowledge base and generate responses based off the retrieved data . 

You can apply filters to document fields/attributes to help you further improve
 the relevancy of responses. Your data sources can include document metadata
 attributes/fields to filter on and can specify which fields to include in the
 embeddings. 

For example, "epoch_modification_time" represents the time in number of seconds since 
 January 1, 1970 (UTC) when the document was last updated. You can filter
 on the most recent data, where "epoch_modification_time" is greater
 than a certain number. These most recent documents can be used for
 the query. 

To use filters when querying a knowledge base, check that your knowledge base
 fulfills the following requirements: 

When configuring your data source connector, most connectors crawl the
 main metadata fields of your documents. If you're using an Amazon S3 bucket as
 your data source, the bucket must include at least one fileName.extension.metadata.json for the file or document
 it's associated with. See Document metadata fields in Connection configuration for more information about
 configuring the metadata file. 

If your knowledge base's vector index is in an Amazon OpenSearch Serverless vector store, check
 that the vector index is configured with the faiss engine. If
 the vector index is configured with the nmslib engine, you'll
 have to do one of the following: 

Create a new knowledge
 base in the console and let Amazon Bedrock automatically create a
 vector index in Amazon OpenSearch Serverless for you. 

Create another vector
 index in the vector store and select faiss as the Engine . Then Create a new knowledge
 base and specify the new vector index. 

If your knowledge base uses a vector index in an S3 vector bucket, you cannot 
 use the startsWith and stringContains filters. 

If you're adding metadata to an existing vector index in an Amazon Aurora
 database cluster, we recommend that you provide the field 
 name of the custom metadata column to store all your metadata in a single column.
 During data ingestion ,
 this column will be used to populate all the information in your metadata files 
 from your data sources. If you choose to provide this field, you must create
 an index on this column. 

When you create a new knowledge
 base in the console and let Amazon Bedrock configure your Amazon Aurora 
 database, it will automatically create a single column for you and populate it with the
 information from your metadata files. 

When you choose to create another vector
 index in the vector store, you must provide the custom metadata field name
 to store information from your metadata files. 
 If you don't provide this field name, you must create a column for
 each metadata attribute in your files and specify the data type (text,
 number, or boolean). For example, if the attribute genre exists in your data source, you would add a column named genre and specify text as the data type. During 
 ingestion, these separate columns
 will be populated with the corresponding attribute values. 

If you have PDF documents in your data source and use Amazon OpenSearch Serverless for your vector
 store: Amazon Bedrock knowledge bases will generate document page numbers and store them in a
 metadata field/attribute called x-amz-bedrock-kb-document-page-number . Note that page
 numbers stored in a metadata field is not supported if you choose no chunking for
 your documents. 

You can use the following filtering operators to filter results when you query: 
Filtering operators 
Operator Console API filter name Supported attribute data types Filtered results 
Equals = equals string, number, boolean Attribute matches the value you provide 
Not equals != notEquals string, number, boolean Attribute doesn’t match the value you provide 
Greater than > greaterThan number Attribute is greater than the value you provide 
Greater than or equals >= greaterThanOrEquals number Attribute is greater than or equal to the value you provide 
Less than < lessThan number Attribute is less than the value you provide 
Less than or equals <= lessThanOrEquals number Attribute is less than or equal to the value you provide 
In : in string list Attribute is in the list you provide (currently best supported with Amazon OpenSearch Serverless and Neptune Analytics 
 GraphRAG vector stores) 
Not in !: notIn string list Attribute isn’t in the list you provide (currently best supported with Amazon OpenSearch Serverless and Neptune Analytics 
 GraphRAG vector stores) 
String contains Not available stringContains string Attribute must be a string. Attribute name matches the key and whose value is a string that contains the value that you provided 
 as a substring, or a list with a member that contains the value that you provided as a substring (currently best supported with Amazon OpenSearch 
 Serverless vector store. The Neptune Analytics GraphRAG vector store supports the string variant but not the list variant of this filter). 
List contains Not available listContains string Attribute must be a string list. Attribute name matches the key and whose value is a list that contains the value that
 you provided as one of its members (currently best supported with Amazon OpenSearch Serverless vector stores). 

To combine filtering operators, you can use the following logical operators: 
Logical operators 
Operator Console API filter field name Filtered results 
And and andAll Results fulfill all of the filtering expressions in the group 
Or or orAll Results fulfill at least one of the filtering 
 expressions in the group 

To learn how to filter results using metadata, choose the tab for your preferred method, and then follow the steps: 
Console 
Follow the console steps at Query a knowledge base and retrieve data or Query a knowledge base and generate responses based off the retrieved data . When you open the Configurations pane, you'll see a Filters section . The following procedures
 describe different use cases: 

To add a filter, create a filtering expression by entering a
 metadata attribute, filtering operator, and value in the box.
 Separate each part of the expression with a whitespace. Press Enter to add the
 filter. 

For a list of accepted filtering operators, see the Filtering operators table above. You
 can also see a list of filtering operators when you add a
 whitespace after the metadata attribute. 

Note 

You must surround strings with quotation marks. 

For example, you can filter for results from source documents
 that contain a genre metadata attribute whose value
 is "entertainment" by adding the following filter: genre = "entertainment" . 

To add another filter, enter another filtering expression in
 the box and press Enter . You
 can add up to 5 filters in the group. 

By default, the query will return results that fulfill all the
 filtering expressions you provide. To return results that
 fulfill at least one of the filtering expressions, choose the and dropdown menu between any two
 filtering operations and select or . 

To combine different logical operators, select + Add
 Group to add a filter group. Enter filtering
 expressions in the new group. You can add up to
 5 filter groups. 

To change the logical operator used between all the filtering
 groups, choose the AND dropdown menu
 between any two filter groups and select OR . 

To edit a filter, select it, modify the filtering operation,
 and choose Apply . 

To remove a filter group, choose the trash can icon
 ( ) next to the group. To remove a filter, choose the
 delete icon ( ) next to the filter. 

The following image shows an example filter configuration that returns
 all documents written after 2018 whose genre is "entertainment" , in addition to documents
 whose genre is "cooking" or "sports" and whose author starts with "C" . 

API 
When you make a Retrieve or RetrieveAndGenerate request, include a retrievalConfiguration field, mapped to a KnowledgeBaseRetrievalConfiguration object. To see the location of this field, refer to the Retrieve and RetrieveAndGenerate request bodies in the API reference. 

The following JSON objects show the minimal fields required in the KnowledgeBaseRetrievalConfiguration object to set filters for different use cases: 

Use one filtering operator (see the Filtering operators table above). 

"retrievalConfiguration": { "vectorSearchConfiguration": { "filter": { " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 }
 }
 }
} 

Use a logical operator (see the Logical
 operators table above) to combine up to
 5. 

"retrievalConfiguration": { "vectorSearchConfiguration": { "filter": { " andAll | orAll ": [
 " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 },
 " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 },
 ...
 ]
 }
 }
} 

Use a logical operator to combine up to 5
 filtering operators into a filter group, and a second logical
 operator to combine that filter group with another filtering
 operator. 

"retrievalConfiguration": { "vectorSearchConfiguration": { "filter": { " andAll | orAll ": [
 " andAll | orAll ": [
 " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 },
 " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 },
 ...
 ],
 " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 }
 ]
 }
 }
} 

Combine up to 5 filter groups by embedding
 them within another logical operator. You can create one level
 of embedding. 

"retrievalConfiguration": { "vectorSearchConfiguration": { "filter": { " andAll | orAll ": [
 " andAll | orAll ": [
 " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 },
 " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 },
 ...
 ],
 " andAll | orAll ": [
 " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 },
 " <filter-type> ": { "key": "string",
 "value": "string" | number | boolean | ["string", "string", ...]
 },
 ...
 ]
 ]
 }
 }
} 

The following table describes the filter types that you can
 use: 

Field Supported value data types Filtered results 
equals string, number, boolean Attribute matches the value you provide 
notEquals string, number, boolean Attribute doesn't match the value you provide 
greaterThan number Attribute is greater than the value you
 provide 
greaterThanOrEquals number Attribute is greater than or equal to the value you
 provide 
lessThan number Attribute is less than the value you provide 
lessThanOrEquals number Attribute is less than or equal to the value you
 provide 
in list of strings Attribute is in the list you provide 
notIn list of strings Attribute isn't in the list you provide 
startsWith string Attribute starts with the string you provide (only
 supported for Amazon OpenSearch Serverless vector stores) 

To combine filter types, you can use one of the following logical
 operators: 

Field Maps to Filtered results 
andAll List of up to 5 filter types Results fulfill all of the filtering expressions in
 the group 
orAll List of up to 5 filter types Results fulfill at least one of the filtering
 expressions in the group 

For examples, see Send a query and include filters (Retrieve) and Send a query and include filters
 (RetrieveAndGenerate) . 

Amazon Bedrock Knowledge Base generates and applies a retrieval filter based on the user
 query and a metadata schema. 

Note 

The feature currently only works with Anthropic Claude 3.5 Sonnet. 

The implicitFilterConfiguration is specified in the vectorSearchConfiguration of the Retrieve request body. Include
 the following fields: 

metadataAttributes – In this array, provide schemas
 describing metadata attributes that the model will generate a filter
 for. 

modelArn – The ARN of the model to use. 

The following shows an example of metadata schemas that you can add to the array
 in metadataAttributes . 

[ { "key": "company",
 "type": "STRING",
 "description": "The full name of the company. E.g. `Amazon.com, Inc.`, `Alphabet Inc.`, etc"
 }, { "key": "ticker",
 "type": "STRING",
 "description": "The ticker name of a company in the stock market, e.g. AMZN, AAPL"
 }, { "key": "pe_ratio",
 "type": "NUMBER",
 "description": "The price to earning ratio of the company. This is a measure of valuation of a company. The lower the pe ratio, the company stock is considered chearper."
 }, { "key": "is_us_company",
 "type": "BOOLEAN",
 "description": "Indicates whether the company is a US company."
 }, { "key": "tags",
 "type": "STRING_LIST",
 "description": "Tags of the company, indicating its main business. E.g. `E-commerce`, `Search engine`, `Artificial intelligence`, `Cloud computing`, etc"
 }
] 
You can implement safeguards for your knowledge base for your use cases and
 responsible AI policies. You can create multiple guardrails tailored to different
 use cases and apply them across multiple request and response conditions, providing
 a consistent user experience and standardizing safety controls across your knowledge
 base. You can configure denied topics to disallow undesirable topics and content
 filters to block harmful content in model inputs and responses. For more
 information, see Detect and filter harmful content by using Amazon Bedrock Guardrails . 

Note 

Using guardrails with contextual grounding for knowledge bases is currently
 not supported on Claude 3 Sonnet and Haiku. 

For general prompt engineering guidelines, see Prompt engineering concepts . 

Choose the tab for your preferred method, and then follow the steps: 
Console 
Follow the console steps at Query a knowledge base and retrieve data or Query a knowledge base and generate responses based off the retrieved data . In the test window, turn on Generate
 responses . Then, in the Configurations pane, expand the Guardrails section. 

In the Guardrails section, choose the Name and the Version of your guardrail. If you would
 like to see the details for your chosen guardrail and version,
 choose View . 

Alternatively, you can create a new one by choosing the Guardrail link. 

When you're finished editing, choose Save
 changes . To exit without saving choose Discard changes . 

API 
When you make a RetrieveAndGenerate request, include the guardrailConfiguration field within the generationConfiguration to use your guardrail with the
 request. To see the location of this field, refer to the RetrieveAndGenerate request body in the API reference. 

The following JSON object shows the minimal fields required in the GenerationConfiguration to set the guardrailConfiguration : 

"generationConfiguration": { "guardrailConfiguration": { "guardrailId": " string ",
 "guardrailVersion": " string "
 }
} 
Specify the guardrailId and guardrailVersion of your chosen guardrails. 

You can use a reranker model to rerank results from knowledge base query.
 Follow the console steps at Query a knowledge base and retrieve data or Query a knowledge base and generate responses based off the retrieved data . When you open the Configurations pane, expand
 the Reranking section. Select a reranker model, update
 permissions if necessary, and modify any additional options. Enter a prompt and
 select Run to test the results after reranking. 

Query decomposition is a technique used to break down a complex queries into
 smaller, more manageable sub-queries. This approach can help in retrieving more
 accurate and relevant information, especially when the initial query is multifaceted
 or too broad. Enabling this option may result in multiple queries being executed
 against your Knowledge Base, which may aid in a more accurate final response. 

For example, for a question like “Who scored higher in the 2022 FIFA
 World Cup, Argentina or France?” , Amazon Bedrock knowledge bases may first
 generate the following sub-queries, before generating a final answer: 

How many goals did Argentina score in the 2022 FIFA World Cup
 final? 

How many goals did France score in the 2022 FIFA World Cup
 final? 

Console 

Create and sync a data source or use an existing knowledge
 base. 

Go to the test window and open the configuration panel. 

Enable query decomposition. 

API 

POST /retrieveAndGenerate HTTP/1.1
Content-type: application/json { "input": { "text": "string"
 },
 "retrieveAndGenerateConfiguration": { "knowledgeBaseConfiguration": { "orchestrationConfiguration": { // Query decomposition
 "queryTransformationConfiguration": { "type": "string" // enum of QUERY_DECOMPOSITION
 }
 },
...}
} 
When generating responses based off retrieval of information, you can use inference parameters to gain more control
 over the model's behavior during inference and influence the model's outputs. 

To learn how to modify the inference parameters, choose the tab for your preferred method, and then follow the steps: 
Console 
To modify inference parameters when querying a
 knowledge base – Follow the console steps at Query a knowledge base and retrieve data or Query a knowledge base and generate responses based off the retrieved data . When you open
 the Configurations pane, you'll see an Inference parameters section. Modify the
 parameters as necessary. 

To modify inference parameters when chatting
 with your document – Follow the steps at Chat with your document without a knowledge base configured . In the Configurations pane, expand the Inference parameters section and modify the
 parameters as necessary. 
API 
You provide the model parameters in the call to the RetrieveAndGenerate API. You can customize the model by providing
 inference parameters in the inferenceConfig field of either
 the knowledgeBaseConfiguration (if you query a knowledge
 base) or the externalSourcesConfiguration (if you chat with your
 document ). 

Within the inferenceConfig field is a textInferenceConfig field that contains the following
 parameters that you can: 

temperature 

topP 

maxTokenCount 

stopSequences 

You can customize the model by using the following parameters in the inferenceConfig field of both externalSourcesConfiguration and knowledgeBaseConfiguration : 

temperature 

topP 

maxTokenCount 

stopSequences 

For a detailed explanation of the function of each of these
 parameters, see Influence response generation with inference parameters . 

Additionally, you can provide custom parameters not supported by textInferenceConfig via the additionalModelRequestFields map. You can provide
 parameters unique to specific models with this argument, for the unique
 parameters see Inference request parameters and response fields for foundation models . 

If a parameter is omitted from textInferenceConfig , a
 default value will be used. Any parameters not recognized in textInferneceConfig will be ignored, while any
 parameters not recognized in AdditionalModelRequestFields will cause an exception. 

A validation exception is thrown if there is the same parameter in
 both additionalModelRequestFields and TextInferenceConfig . 

Using model parameters in
 RetrieveAndGenerate 

The following is an example of the structure for inferenceConfig and additionalModelRequestFields under the generationConfiguration in the RetrieveAndGenerate request body: 

"inferenceConfig": { "textInferenceConfig": { "temperature": 0.5, 
 "topP": 0.5,
 "maxTokens": 2048,
 "stopSequences": ["\nObservation"]
 }
},
"additionalModelRequestFields": { "top_k": 50
} 
The proceeding example sets a temperature of 0.5, top_p of 0.5, maxTokens of 2048, stops
 generation if it encounters the string "\nObservation" in the generated
 response, and passes a custom top_k value of 50. 

When you query a knowledge base and request response generation, Amazon Bedrock uses a
 prompt template that combines instructions and context with the user query to
 construct the generation prompt that's sent to the model for response generation.
 You can also customize the orchestration prompt, which turns the user's prompt into
 a search query. You can engineer the prompt templates with the following
 tools: 

Prompt placeholders – Pre-defined
 variables in Amazon Bedrock Knowledge Bases that are dynamically filled in at runtime during knowledge
 base query. In the system prompt, you'll see these placeholders surrounded
 by the $ symbol. The following list describes the placeholders
 you can use: 

Note 

The $output_format_instructions$ placeholder is a
 required field for citations to be displayed in the response. 

Variable Prompt template Replaced by Model Required? 
$query$ Orchestration, generation The user query sent to the knowledge
 base. Anthropic Claude Instant, Anthropic Claude
 v2.x Yes 
Anthropic Claude 3 Sonnet No (automatically included in model input) 
$search_results$ Generation The retrieved results for the user query. All Yes 
$output_format_instructions$ Orchestration Underlying instructions for formatting the response
 generation and citations. Differs by model. If you define
 your own formatting instructions, we suggest that you remove
 this placeholder. Without this placeholder, the response
 won't contain citations. All Yes 
$current_time$ Orchestration, generation The current time. All No 

XML tags – Anthropic models
 support the use of XML tags to structure and delineate your prompts. Use
 descriptive tag names for optimal results. For example, in the default
 system prompt, you'll see the <database> tag used to
 delineate a database of previously asked questions). For more information,
 see Use XML
 tags in the Anthropic user guide . 

For general prompt engineering guidelines, see Prompt engineering concepts . 

Choose the tab for your preferred method, and then follow the steps: 
Console 
Follow the console steps at Query a knowledge base and retrieve data or Query a knowledge base and generate responses based off the retrieved data . In the test window, turn on Generate
 responses . Then, in the Configurations pane, expand the Knowledge base prompt template section. 

Choose Edit . 

Edit the system prompt in the text editor, including prompt
 placeholders and XML tags as necessary. To revert to the default
 prompt template, choose Reset to
 default . 

When you're finished editing, choose Save
 changes . To exit without saving the system
 prompt, choose Discard changes . 

API 
When you make a RetrieveAndGenerate request, include a generationConfiguration field, mapped to a GenerationConfiguration object. To see the location of this field, refer to the RetrieveAndGenerate request body in the API reference. 

The following JSON object shows the minimal fields required in the GenerationConfiguration object to set the maximum number of retrieved results to
 return: 

"generationConfiguration": { "promptTemplate": { "textPromptTemplate": "string"
 }
} 
Enter your custom prompt template in the textPromptTemplate field, including prompt placeholders
 and XML tags as necessary. For the maximum number of characters allowed
 in the system prompt, see the textPromptTemplate field in GenerationConfiguration . 

Document Conventions 
Query a knowledge base connected to an Amazon Neptune Analytics graph 
Configure responses for reasoning models 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
