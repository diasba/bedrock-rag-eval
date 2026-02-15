# Query a knowledge base and generate responses based off the retrieved data - Amazon Bedrock Query a knowledge base and generate responses based off the retrieved data - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve-generate.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Query a knowledge base and generate responses based off the retrieved data - Amazon Bedrock 
Query a knowledge base and generate responses based off the retrieved data - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Query a knowledge base and generate responses based off the retrieved data 

Important 

Guardrails are applied only to the input and the generated response from the LLM. They are not applied to the references
 retrieved from Knowledge Bases at runtime. 

After your knowledge base is set up, you can query it and generate responses based on the chunks retrieved from your source data by using the RetrieveAndGenerate API operation. The responses are returned with citations to the original source data. You can also use a reranking model instead of the default Amazon Bedrock Knowledge Bases ranker to rank source chunks for relevance during retrieval. 

Multimodal content limitations 

RetrieveAndGenerate has limited support for multimodal content. When using Nova Multimodal Embeddings, RAG functionality is restricted to text content only. For full multimodal support including audio and video processing, use BDA with text embedding models. For details, see Build a knowledge base for multimodal content . 

Note 

Images returned from the Retrieve response during the RetrieveAndGenerate flow are included in the prompt for response generation. The RetrieveAndGenerate response can't include images, but it can cite the sources that contain the images. 

To learn how to query your knowledge base, choose the tab for your preferred method, and then follow the steps: 
Console 
To test your knowledge base 

Sign in to the AWS Management Console with an IAM identity that has permissions to use the Amazon Bedrock console. Then, open the Amazon Bedrock console at https://console.aws.amazon.com/bedrock . 

In the left navigation pane, choose Knowledge bases . 

In the Knowledge bases section, do one of the following actions: 

Choose the radio button next to the knowledge base you want to test and select Test knowledge base . A test window expands from the right. 

Choose the knowledge base that you want to test. A test window expands from the right. 

To generate responses based on information retrieved from your knowledge base, turn on Generate responses for your query . Amazon Bedrock will generate responses based on your data sources and cites the information it provides with footnotes. 

To choose a model to use for response generation, choose Select model . Then select Apply . 

(Optional) Select the configurations icon ( ) to open up Configurations . For information about configurations, see Configure and customize queries and response
 generation . 

Enter a query in the text box in the chat window and select Run to return responses from the knowledge base. 

Select a footnote to see an excerpt from the cited source for that part of the response. Choose the link to navigate to the S3 object containing the file. 

To see details about the returned chunks, select Show source details . 

To see the configurations that you set for query, expand Query configurations . 

To view details about a source chunk, expand it by choosing the right arrow ( ) next to it. You can see the following information: 

The raw text from the source chunk. To copy this text, choose the copy icon ( ). If you used Amazon S3 to store your data, choose the external link icon ( ) to navigate to the S3 object containing the file. 

The metadata associated with the source chunk, if you used Amazon S3 to store your data. The attribute/field keys and values are defined in the .metadata.json file that's associated with the source document. For more information, see the Metadata and filtering section in Configure and customize queries and response
 generation . 

Chat options 

To use a different model for response generation, Select Change model . If you change the model, the text in the chat window will be completely cleared. 

Switch to retrieving source chunks directly by clearing Generate responses . If you change the setting, the text in the chat window will be completely cleared. 

To clear the chat window, select the broom icon ( ). 

To copy all the output in the chat window, select the copy icon ( ). 

API 
To query a knowledge base and use a foundation model to generate responses based off the results from the data sources, send a RetrieveAndGenerate request with a Agents for Amazon Bedrock runtime endpoint . 

The RetrieveAndGenerateStream API returns data in a streaming format and allows you to access the generated responses in chunks without waiting for the entire result. 

The following fields are required: 

Note 

The API response contains citation events. The citation member has been deprecated. We recommend that you use the generatedResponse and retrievedReferences fields instead. For reference, see CitationEvent . 

Field Basic description 
input Contains a text field to specify the
 query. 
retrieveAndGenerateConfiguration Contains a RetrieveAndGenerateConfiguration , which specifies configurations for retrieval and generation. See below for more details. 

The following fields are optional: 

Field Use case 
sessionId Use the same value as a previous session to continue that session
 and maintain context from it for the model. 
sessionConfiguration To include a custom KMS key for encryption of the
 session. 

Include the knowledgeBaseConfiguration field in the RetrieveAndGenerateConfiguration . This field maps to a KnowledgeBaseRetrieveAndGenerateConfiguration object, which contains the following fields: 

The following fields are required: 

Field Basic description 
knowledgeBaseId The ID of the knowledge base to query. 
modelArn The ARN of the foundation model or inference profile to use for generation. 

The following fields are optional: 

Field Use case 
retrievalConfiguration To include query
 configurations for customizing the vector
 search. For more information, see KnowledgeBaseRetrievalConfiguration . 
orchestrationConfiguration To specify configurations for how the model processes the prompt prior to retrieval and generation. 
 For more information, see OrchestrationConfiguration . 
generationConfiguration To specify configurations for response generation. For more information, see GenerationConfiguration . 

You can use a reranking model over the default Amazon Bedrock Knowledge Bases ranking model by including the rerankingConfiguration field in the KnowledgeBaseVectorSearchConfiguration within the KnowledgeBaseRetrievalConfiguration . The rerankingConfiguration field maps to a VectorSearchRerankingConfiguration object, in which you can specify the reranking model to use, any additional request fields to include, metadata attributes to filter out documents during reranking, and the number of results to return after reranking. For more information, see VectorSearchRerankingConfiguration . 

Note 

If you the numberOfRerankedResults value that you specify is greater than the numberOfResults value in the KnowledgeBaseVectorSearchConfiguration , the maximum number of results that will be returned is the value for numberOfResults . An exception is if you use query decomposition (for more information, see the Query modifications section in Configure and customize queries and response
 generation . If you use query decomposition, the numberOfRerankedResults can be up to five times the numberOfResults . 

The response returns the generated response in the output field and the cited source chunks as an array in the citations field. Each Citation object contains the following fields. 

Field Basic description 
generatedResponsePart In the textResponsePart field, the text that the citation pertains to is included. The span field provides the indexes for the beginning and end of the part of the output that has a citation. 
retrievedReferences An array of RetrievedReference objects, each of which contains the content of a source chunk, metadata associated with the document, and the URI or URL location of the document in the data source. If the content is an image, the data URI of the base64-encoded content is returned in the following format: data:image/jpeg;base64, $ { base64-encoded string} . 

The response also returns a sessionId value, which you can reuse in another request to maintain the same conversation. 

If you included a guardrailConfiguration in the request, the guardrailAction field informs you if the content was blocked or not. 

If the retrieved data contains images, the response also returns the following response headers, which contain metadata for source chunks returned in the response: 

x-amz-bedrock-kb-byte-content-source – Contains the Amazon S3 URI of the image. 

x-amz-bedrock-kb-description – Contains the base64-encoded string for the image. 

Note 

You can't filter on these metadata response headers when configuring metadata filters . 

Note 

If you receive an error that the prompt exceeds the character limit while generating responses, you can shorten the prompt in the following ways: 

Reduce the maximum number of retrieved results (this shortens what is filled in for the $search_results$ placeholder in the Knowledge base prompt templates:
 orchestration & generation ). 

Recreate the data source with a chunking strategy that uses smaller chunks (this shortens what is filled in for the $search_results$ placeholder in the Knowledge base prompt templates:
 orchestration & generation ). 

Shorten the prompt template. 

Shorten the user query (this shortens what is filled in for the $query$ placeholder in the Knowledge base prompt templates:
 orchestration & generation ). 

Document Conventions 
Query a knowledge base and retrieve
 data 
Generate a query for structured data 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
