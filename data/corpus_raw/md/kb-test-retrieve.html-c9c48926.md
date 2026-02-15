# Query a knowledge base and retrieve data - Amazon Bedrock Query a knowledge base and retrieve data - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Query a knowledge base and retrieve data - Amazon Bedrock 
Query a knowledge base and retrieve data - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Query a knowledge base and retrieve data 

Important 

Guardrails are applied only to the input and the generated response from the LLM. They
 are not applied to the references retrieved from Knowledge Bases at runtime. 

After your knowledge base is set up, you can query it and retrieve chunks from your source
 data that is relevant to the query by using the Retrieve API operation. You can also use a reranking model instead of the default Amazon Bedrock Knowledge Bases ranker to rank
 source chunks for relevance during retrieval. 

To learn how to query your knowledge base, choose the tab for your preferred method, and then follow the steps: 
Console 
To test your knowledge base 

Sign in to the AWS Management Console with an IAM identity that has permissions to use the Amazon Bedrock console. Then, open the Amazon Bedrock console at https://console.aws.amazon.com/bedrock . 

In the left navigation pane, choose Knowledge bases . 

In the Knowledge bases section, do one of
 the following actions: 

Choose the radio button next to the knowledge base you want to
 test and select Test knowledge base . A test
 window expands from the right. 

Choose the knowledge base that you want to test. A test window
 expands from the right. 

In the test window, clear Generate responses for your
 query to return information retrieved directly from your
 knowledge base. 

(Optional) Select the configurations icon ( ) to open up Configurations . For information about
 configurations, see Configure and customize queries and response
 generation . 

Enter a query in the text box in the chat window and select Run to return responses from the knowledge
 base. 

The source chunks are returned directly in order of relevance. Images extracted from your data source can also be returned as a
 source chunk. 

To see details about the returned chunks, select Show source details . 

To see the configurations that you set for query, expand Query configurations . 

To view details about a source chunk, expand it by choosing the right arrow ( ) next to it. You can see the following information: 

The raw text from the source chunk. To copy this text, choose the copy icon ( ). If you used Amazon S3 to store your data, choose the external link icon ( ) to navigate to the S3 object containing the file. 

The metadata associated with the source chunk, if you used Amazon S3 to store your data. The attribute/field keys and values are defined in the .metadata.json file that's associated with the source document. For more information, see the Metadata and filtering section in Configure and customize queries and response
 generation . 

Chat options 

Switch to generating responses based on the retrieved source chunks by
 turning on Generate responses . If you change the
 setting, the text in the chat window will be completely cleared. 

To clear the chat window, select the broom icon ( ). 

To copy all the output in the chat window, select the copy icon
 ( ). 

API 
To query a knowledge base and only return relevant text from data sources,
 send a Retrieve request with an Agents for Amazon Bedrock runtime endpoint . 

The following fields are required: 

Field Basic description 
knowledgeBaseId To specify the knowledge base to query. 
retrievalQuery Contains a text field to specify the
 query. 
guardrailsConfiguration Include guardrailsConfiguration fields such as guardrailsId and guardrailsVersion to use your guardrail with the request 

The following fields are optional: 

Field Use case 
nextToken To return the next batch of responses (see response fields
 below). 
retrievalConfiguration To include query
 configurations for customizing the vector search. See KnowledgeBaseVectorSearchConfiguration for more information. 

You can use a reranking model over the default Amazon Bedrock Knowledge Bases ranking model by including
 the rerankingConfiguration field in the KnowledgeBaseVectorSearchConfiguration . The rerankingConfiguration field maps to a VectorSearchRerankingConfiguration object, in which you can specify the reranking model to use, any additional
 request fields to include, metadata attributes to filter out documents during
 reranking, and the number of results to return after reranking. For more
 information, see VectorSearchRerankingConfiguration . 

Note 

If you the numberOfRerankedResults value that you specify is greater than the numberOfResults value in the KnowledgeBaseVectorSearchConfiguration , the maximum number of results that will be returned is the value for numberOfResults . An exception is if you use query decomposition (for more information, see the Query modifications section in Configure and customize queries and response
 generation . If you use query decomposition, the numberOfRerankedResults can be up to five times the numberOfResults . 

The response returns the source chunks from the data source as an array of KnowledgeBaseRetrievalResult objects in the retrievalResults field. Each KnowledgeBaseRetrievalResult contains the following fields: 

Field Description 
content Contains a text source chunk in the text or an image source chunk in the byteContent field. If the content is an image, the data URI of the base64-encoded content is returned in the following format: data:image/jpeg;base64, $ { base64-encoded string} . 
metadata Contains each metadata attribute as a key and the metadata
 value as a JSON value that the key maps to. 
location Contains the URI or URL of the document that the source chunk
 belongs to. 
score The relevancy score of the document. You can use this score
 to analyze the ranking of results. 

If the number of source chunks exceeds what can fit in the response, a value
 is returned in the nextToken field. Use that value in another
 request to return the next batch of results. 

If the retrieved data contains images, the response also returns the following response headers, which contain metadata for source chunks returned in the response: 

x-amz-bedrock-kb-byte-content-source – Contains the Amazon S3 URI of the image. 

x-amz-bedrock-kb-description – Contains the base64-encoded string for the image. 

Note 

You can't filter on these metadata response headers when configuring metadata filters . 

Multimodal queries 
For knowledge bases using multimodal embedding models, you can query with
 either text or images. The retrievalQuery field supports a multimodalInputList field for image queries: 

Note 

For comprehensive guidance on setting up and working with multimodal
 knowledge bases, including choosing between Nova and BDA approaches, see Build a knowledge base for multimodal content . 

You can query with images by using the multimodalInputList field: 

{ "knowledgeBaseId": "EXAMPLE123", 
 "retrievalQuery": { "multimodalInputList": [ { "content": { "byteContent": "base64-encoded-image-data"
 },
 "modality": "IMAGE"
 }
 ]
 }
} 
Or you can query with text only by using the text field: 

{ "knowledgeBaseId": "EXAMPLE123",
 "retrievalQuery": { "text": "Find similar shoes"
 }
} 
Common multimodal query patterns 
Following are some common query patterns: 
Image-to-image search 
Upload an image to find visually similar images. Example: Upload a
 photo of a red Nike shoe to find similar shoes in your product
 catalog. 
Text-based search 
Use text queries to find relevant content. Example: "Find similar
 shoes" to search your product catalog using text
 descriptions. 
Visual document search 
Search for charts, diagrams, or visual elements within documents.
 Example: Upload a chart image to find similar charts in your
 document collection. 

Choosing between Nova and BDA for multimodal content 
When working with multimodal content, choose your approach based on your
 content type and query patterns: 
Nova vs BDA Decision Matrix 
Content Type Use Nova Multimodal Embeddings Use Bedrock Data Automation (BDA) Parser 
Video Content Visual storytelling focus (sports, ads, demonstrations),
 queries on visual elements, minimal speech content Important speech/narration (presentations, meetings,
 tutorials), queries on spoken content, need transcripts 
Audio Content Music or sound effects identification, non-speech audio
 analysis Podcasts, interviews, meetings, any content with speech
 requiring transcription 
Image Content Visual similarity searches, image-to-image retrieval, visual
 content analysis Text extraction from images, document processing, OCR
 requirements 

Note 

Nova multimodal embeddings cannot process speech content directly. If your
 audio or video files contain important spoken information, use the BDA
 parser to convert speech to text first, or choose a text embedding model
 instead. 

Multimodal query limitations 
Following are some limitations with multimodal queries: 

Maximum of one image per query in the current release 

Image queries are only supported with multimodal embedding models
 (Titan G1 or Cohere Embed v3) 

RetrieveAndGenerate API is not supported for knowledge bases with
 multimodal embedding models and S3 content buckets 

If you provide an image query to a knowledge base using text-only
 embedding models, a 4xx error will be returned 

Multimodal API response structure 
Retrieval responses for multimodal content include additional
 metadata: 

Source URI: Points to your original
 S3 bucket location 

Supplemental URI: Points to the copy
 in your multimodal storage bucket 

Timestamp metadata: Included for
 video and audio chunks to enable precise playback positioning 

Note 

When using the API or SDK, you'll need to handle file retrieval and
 timestamp navigation in your application. The console handles this
 automatically with enhanced video playback and automatic timestamp
 navigation. 

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
Test your knowledge base with queries and responses 
Query a knowledge base and generate responses 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
