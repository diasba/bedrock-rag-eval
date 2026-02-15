# Turning data into a knowledge base - Amazon Bedrock Turning data into a knowledge base - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-how-data.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Turning data into a knowledge base - Amazon Bedrock 
Turning data into a knowledge base - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
Unstructured data Structured data 

Turning data into a knowledge base 

To create a knowledge base, connect to a supported data source that you want your knowledge base to be able to access. Your knowledge base will be able to respond to user queries or generate responses based on the retrieved data. 

Amazon Bedrock Knowledge Bases supports a variety of documents, including text, images, or multimodal documents that contain tables, charts, diagrams, and other images. Multimodal data refers to a combination of text and visual data. Examples of file types that contain unstructured data are text, markdown, HTML, and PDFs. 

The following sections describe the types of data that Amazon Bedrock Knowledge Bases supports and the services that you can connect your knowledge base to for each type of data: 

Unstructured data 
Unstructured data refers to data that isn't forced into a predefined structure. Amazon Bedrock Knowledge Bases supports connecting to the following services to add unstructured data to your knowledge base: 

Amazon S3 

Confluence (preview) 

Microsoft SharePoint (preview) 

Salesforce (preview) 

Web Crawler (preview) 

Custom data source (allows direct ingestion of data into knowledge bases without needing to sync) 

A data source contains the raw form of your documents. To optimize the query process, a knowledge base converts your raw data into vector embeddings , a numerical representation of the data, to quantify similarity to queries that are also converted into vector embeddings. Amazon Bedrock Knowledge Bases uses the following resources in the process of converting your data source: 

Embedding model – A foundation model that converts your data into vector embeddings. For multimodal data containing both text and images, you can use multimodal embedding models like Amazon Titan Multimodal Embeddings G1 or Cohere Embed v3. 

Vector store – A service that stores the vector representation of your data. The following vector stores are supported: 

Amazon OpenSearch Serverless 

Amazon Neptune 

Amazon Aurora (RDS) 

Pinecone 

Redis Enterprise Cloud 

MongoDB Atlas 

The process of converting your data into vector embeddings is called ingestion . The ingestion process that turns your data into a knowledge base involves the following steps: 

Ingestion 

The data is parsed by your chosen parser. For more information about parsing, see Parsing options for your data source . 

Each document in your data source is split into chunks , subdivisions of the data that can be defined by the number of tokens and other parameters. For more information about chunking, see How content chunking works for knowledge bases . 

Your chosen embedding model converts the data into vector embeddings. For multimodal content, images are embedded as visual vectors while text is embedded as text vectors, enabling search across both modalities. 

The vector embeddings are written to a vector index in your chosen vector store. 

After the ingestion process is complete, your knowledge base is ready to be queried. For information about how to query and retrieve information from your knowledge base, see Retrieving information from data sources using Amazon Bedrock Knowledge Bases . 

If you make changes to a data sources, you must sync the changes to ingest additions, modifications, and deletions into the knowledge base. Some data sources support direct ingestion or deletion of files into the knowledge base, eliminating the need to treat data source modification and ingestion as separate steps and the need to always perform full syncs. To learn how to ingest documents directly into your knowledge base and the data sources that support it, see Ingest changes directly into a knowledge base . 

Amazon Bedrock Knowledge Bases offers various options to customize how your data is ingested. For more information about customizing this process, see Customizing your knowledge base . 

Structured data 
Structured data refers to tabular data in a format that is predefined by the data store it exists in. Amazon Bedrock Knowledge Bases connects to supported structured data stores through the Amazon Redshift query engine. Amazon Bedrock Knowledge Bases provides a fully managed mechanism that analyzes query patterns, query history, and schema metadata to convert natural language queries into SQL queries. These converted queries are then used to retrieve relevant information from supported data sources. 

Amazon Bedrock Knowledge Bases supports connecting to the following services to add structured data stores to your knowledge base: 

Amazon Redshift 

AWS Glue Data Catalog (AWS Lake Formation) 

If you connect your knowledge base to a structured data store, you don't need to convert the data into vector embeddings. Instead, Amazon Bedrock Knowledge Bases can directly query the structured data store. During query, Amazon Bedrock Knowledge Bases can convert user queries into SQL queries to retrieve data that is relevant to the user query and generate more accurate responses. You can also generate SQL queries without retrieving data and use them in other workflows. 

As an example, a database repository contains the following table with information about
 customers and their purchases: 

Customer ID Amount purchased in 2020 Amount purchased in 2021 Amount purchased in 2022 Total purchased amount to date 
1 200 300 500 1000 
2 150 100 120 370 
3 300 300 300 900 
4 720 180 100 900 
5 500 400 100 1000 
6 900 800 1000 2700 
7 470 420 400 1290 
8 250 280 250 780 
9 620 830 740 2190 
10 300 200 300 800 

If a user query says "give me a summary of the top 5
 spending customers," the knowledge base can do the following: 

Convert the query into an SQL query. 

Return an excerpt from the table that contains the following: 

Relevant table columns "Customer ID" and "Total Purchased Amount To Date" 

Table rows containing the total purchase amount for the 10 highest spending customers 

Generate a response that states which customers were the top 5 spending customers and how much they purchased. 

Other examples of queries that a knowledge base can generate a table excerpt for include: 

"top 5 customers by spending in 2020" 

"top customer by purchase amount in 2020" 

"top 5 customers by purchase amount from 2020-2022" 

"top 5 highest spending customers in 2020-2022" 

"customers with total purchase amount less than $10" 

"top 5 lowest spending customers" 

The more specific or detailed a query is, the more the knowledge base can narrow down the exact information to return. For example, instead of the query "top 10 customers by spending in 2020", a more specific query is “find the 10 highest total purchased amount to date for customers in 2020". The specific query refers to the column name "Total Purchased Amount To Date" in the customers spending database table, and also indicates that the data should be sorted by "highest". 

Document Conventions 
How knowledge bases work 
Retrieving information from data sources 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
