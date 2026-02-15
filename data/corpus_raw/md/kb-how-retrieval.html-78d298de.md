# Retrieving information from data sources using Amazon Bedrock Knowledge Bases - Amazon Bedrock Retrieving information from data sources using Amazon Bedrock Knowledge Bases - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-how-retrieval.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Retrieving information from data sources using Amazon Bedrock Knowledge Bases - Amazon Bedrock 
Retrieving information from data sources using Amazon Bedrock Knowledge Bases - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Retrieving information from data sources using Amazon Bedrock Knowledge Bases 

After setting up a knowledge base, you can set up your application to query the data sources in it. To query a knowledge base, you can take advantage of the following API operations: 

Retrieve – Retrieves the source chunks or images from your data that are most relevant to the query and returns them in the response as an array. 

RetrieveAndGenerate – Joins Retrieve with the InvokeModel operation in Amazon Bedrock to retrieve the source chunks from your data that are most relevant to the query and generate a natural language response. Includes citations to specific source chunks from the data. If your data source includes visual elements, the model leverage insights from these images when generating a text response and provide source attribution for the images. 

GenerateQuery – Converts natural language user queries into queries that are in a form suitable for the structured data store. 

The RetrieveAndGenerate operation is a combined action that underlyingly uses GenerateQuery (if your knowledge base is connected to a structured data store), Retrieve and InvokeModel to carry out the entire RAG process. Because Amazon Bedrock Knowledge Bases also provides you access to the Retrieve operation, you have the flexibility to decouple the steps in RAG and customize them for your specific use case. 

You can also use a reranking model when using Retrieve or RetrieveAndGenerate to rerank the relevance of documents retrieved during query. 

To learn how to use these API operations when querying a knowledge base, see Test your knowledge base with queries and responses . 

Document Conventions 
Turning data into a knowledge base 
Customizing your knowledge base 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
