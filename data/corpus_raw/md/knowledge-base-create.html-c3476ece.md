# Create a knowledge base by connecting to a data source in Amazon Bedrock Knowledge Bases - Amazon Bedrock Create a knowledge base by connecting to a data source in Amazon Bedrock Knowledge Bases - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Create a knowledge base by connecting to a data source in Amazon Bedrock Knowledge Bases - Amazon Bedrock 
Create a knowledge base by connecting to a data source in Amazon Bedrock Knowledge Bases - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Create a knowledge base by connecting to a data source in Amazon Bedrock Knowledge Bases 

When you create a knowledge base by connecting to a data source, you set up or specify the following: 

General information that defines and identifies the knowledge base 

The service role with permissions to the knowledge base. 

Configurations for the knowledge base, including the embeddings model to use when converting data from the data source, storage configurations for the service in which to store the embeddings, and, optionally, an S3 location to store multimodal data. 

Note 

You can’t create a knowledge base with a root user. Log in with an IAM user before starting these steps. 

Expand the section that corresponds to your use case: 

To set up a knowledge base 

Sign in to the AWS Management Console with an IAM identity that has permissions to use the Amazon Bedrock console. Then, open the Amazon Bedrock console at https://console.aws.amazon.com/bedrock . 

In the left navigation pane, choose Knowledge bases . 

In the Knowledge bases section, choose the create button and select to create a knowledge base with a vector store. 

(Optional) Change the default name and provide a description for your knowledge base. 

Choose an AWS Identity and Access Management (IAM) role that provides Amazon Bedrock
 permission to access other required AWS services. You can let Amazon Bedrock create the service role or 
 choose to use your own custom role that you created for
 Neptune Analytics . 

Choose a data source to connect your knowledge base to. 

(Optional) Add tags to your knowledge base. For more information, see Tagging Amazon Bedrock resources . 

(Optional) Configure services for which to deliver activity logs for your knowledge base. 

Go to the next section and follow the steps at Connect a data source to your knowledge base to configure a data source. 

In the Embeddings model section, do the following: 

Choose an embeddings model to convert your data into vector embeddings. For multimodal data (images, audio, and video), select a multimodal embedding model such as Amazon Titan Multimodal Embeddings G1 or Cohere Embed v3. 

Note 

When using Amazon Titan Multimodal Embeddings G1, you must provide an S3 content bucket and can only use the default parser. This model is optimized for image search use cases. For comprehensive guidance on choosing between multimodal approaches, see Build a knowledge base for multimodal content . 

(Optional) Expand the Additional configurations section to see the following configuration options (not all models support all configurations): 

Embeddings type – Whether to convert the data to floating-point (float32) vector embeddings (more precise, but more costly) or binary vector embeddings (less precise, but less costly). To learn about which embeddings models support binary vectors, refer to supported embeddings models . 

Vector dimensions – Higher values improve accuracy but increase cost and latency. 

In the Vector database section, do the following: 

Choose a vector store to store the vector embeddings that will be used for query. You have the following options: 

Quick create a new vector store – choose one of the available
 vector stores for Amazon Bedrock to create. You can also optionally configure AWS KMS key encryption for your
 vector store. 

Note 

When using this option, Amazon Bedrock automatically handles the metadata placement for each vector store. 

Amazon OpenSearch Serverless – Amazon Bedrock Knowledge Bases creates an Amazon OpenSearch Serverless vector search collection and index and configures it with the required fields for you. 

Amazon Aurora PostgreSQL Serverless – Amazon Bedrock sets up an Amazon Aurora PostgreSQL Serverless vector store. This process takes unstructured text data from
 an Amazon S3 bucket, transforms it into text chunks and vectors, and then stores them in a PostgreSQL database. For more information, see Quick create an Aurora PostgreSQL Knowledge Base for Amazon Bedrock . 

Amazon Neptune Analytics – Amazon Bedrock uses Retrieval Augmented Generation (RAG) techniques combined with graphs to enhance generative AI applications so that end users can get more accurate and comprehensive responses. 

Amazon S3 Vectors – Amazon Bedrock Knowledge Bases creates an S3 vector bucket and a vector index that will store the embeddings 
 generated from your data sources. 

You can create a knowledge base for Amazon S3 Vectors in all AWS Regions where both Amazon Bedrock and
 Amazon S3 Vectors are available. For region availability information, see Amazon S3 Vectors in the Amazon S3 User Guide . 

Note 

When using Amazon S3 Vectors with Amazon Bedrock Knowledge Bases, you can attach up to 1 KB of custom metadata (including both filterable and non-filterable metadata) and 35 metadata keys per vector. For detailed information about metadata limitations, see Metadata support in Prerequisites for using a vector store you created for a
 knowledge base . 

Choose a vector store you have created – Select a supported vector store and identify the vector field names and metadata
 field names in the vector index. For more information, see Prerequisites for using a vector store you created for a
 knowledge base . 

Note 

If your data source is a Confluence, Microsoft SharePoint, or Salesforce instance, the only supported vector store service is Amazon OpenSearch Serverless. 

(Optional) Expand the Additional configurations section and modify any relevant configurations. 

If your data source contains images, specify an Amazon S3 URI in which to store the images that the parser will extract from the data in the Multimodal storage destination . The images can be returned during query. You can also optionally choose a customer managed key instead of the default AWS managed key to encrypt your data. 

Note 

Multimodal data is only supported with Amazon S3 and custom data sources. 

Note 

When using multimodal embedding models: 

Amazon Titan Multimodal Embeddings G1 requires an S3 content bucket and works best with image-only datasets using the default parser 

Cohere Embed v3 supports mixed text and image datasets and can be used with any parser configuration 

For image search use cases, avoid using Bedrock Data Automation (BDA) or foundation model parsers with Titan G1 due to token limitations 

The multimodal storage destination creates file copies for retrieval purposes, which can incur additional storage charges 

Choose Next and review the details of your knowledge base. You can edit any 
 section before going ahead and creating your knowledge base. 

Note 

The time it takes to create the knowledge base depends on your specific configurations. 
 When the creation of the knowledge base has completed, the status of the knowledge base changes to 
 either state it is ready or available. 

Once your knowledge base is ready and available, sync your data source 
 for the first time and whenever you want to keep your content up to date. 
 Select your knowledge base in the console and select Sync within 
 the data source overview section. 

To create a knowledge base, send a CreateKnowledgeBase request with an Agents for Amazon Bedrock build-time endpoint . 

Note 

If you prefer to let Amazon Bedrock create and manage a vector store for you, use the console. For more information, expand the Use the console section in this topic. 

The following fields are required: 

Field Basic description 
name A name for the knowledge base 
roleArn The ARN of an Amazon Bedrock Knowledge Bases service role . 
knowledgeBaseConfiguration Contains configurations for the knowledge base. See details below. 
storageConfiguration (Only required if you're connecting to an unstructured data source). Contains configurations for the data source service that you choose. 

The following fields are optional: 

Field Use case 
description A description for the knowledge base. 
clientToken To ensure the API request completes only once. For more information, see Ensuring idempotency . 
tags To associate tags with the flow. For more information, see Tagging Amazon Bedrock resources . 

In the knowledgeBaseConfiguration field, which maps to a KnowledgeBaseConfiguration object, specify VECTOR in the type field and include a VectorKnowledgeBaseConfiguration object. In the object, include the following fields: 

embeddingModelArn – The ARN of the embedding model to use. 

embeddingModelConfiguration – Configurations for the embedding model. To see the possible values you can specify for each supported model, see Supported models and Regions for Amazon Bedrock knowledge bases . 

(If you plan to include multimodal data, which includes images, figures, charts, or tables, in your knowledge base) supplementalDataStorageConfiguration – Maps to a SupplementalDataStorageLocation object, in which you specify the S3 location in which to store the extracted data. For more information, see Parsing options for your data source . 

In the storageConfiguration field, which maps to a StorageConfiguration object, specify the vector store that you plan to connect to in the type field and include the field that corresponds to that vector store. See each vector store configuration type at StorageConfiguration for details about the information you need to provide. 

The following shows an example request to create a knowledge base connected to an Amazon OpenSearch Serverless collection. The data from connected data sources will be converted into binary vector embeddings with Amazon Titan Text Embeddings V2 and multimodal data extracted by the parser is set up to be stored in a bucket called MyBucket . 

PUT /knowledgebases/ HTTP/1.1
Content-type: application/json { "name": "MyKB",
 "description": "My knowledge base",
 "roleArn": "arn:aws:iam::111122223333:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase_123",
 "knowledgeBaseConfiguration": { "type": "VECTOR",
 "vectorKnowledgeBaseConfiguration": { "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0",
 "embeddingModelConfiguration": { "bedrockEmbeddingModelConfiguration": { "dimensions": 1024,
 "embeddingDataType": "BINARY"
 }
 },
 "supplementalDataStorageConfiguration": { "storageLocations": [ { "s3Location": { "uri": "arn:aws:s3:::MyBucket"
 },
 "type": "S3"
 }
 ]
 }
 }
 },
 "storageConfiguration": { "opensearchServerlessConfiguration": { "collectionArn": "arn:aws:aoss:us-east-1:111122223333:collection/abcdefghij1234567890",
 "fieldMapping": { "metadataField": "metadata",
 "textField": "text",
 "vectorField": "vector"
 },
 "vectorIndexName": "MyVectorIndex"
 }
 }
} 

Topics 

Connect a data source to your knowledge base 

Customize ingestion for a data source 

Set up security configurations for your knowledge base 

Document Conventions 
Configuring OpenSearch permissions
 with fine-grained access control 
Connect a data source 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
