# Use a custom transformation Lambda function to define how your data is ingested - Amazon Bedrock Use a custom transformation Lambda function to define how your data is ingested - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-custom-transformation.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Use a custom transformation Lambda function to define how your data is ingested - Amazon Bedrock 
Use a custom transformation Lambda function to define how your data is ingested - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Use a custom transformation Lambda function to define how your data is ingested 

You have the ability to define a custom transformation Lambda function to inject 
 your own logic into the knowledge base ingestion process. 

You may have specific chunking logic, not natively supported by Amazon Bedrock knowledge bases. Use the 
 no chunking strategy option, while specifying a Lambda function that contains your chunking logic. 
 Additionally, you'll need to specify an Amazon S3 bucket for the knowledge base to write files to be chunked 
 by your Lambda function. 

After chunking, your Lambda function will write back chunked files into the 
 same bucket and return references for the knowledge base for further processing. You optionally have 
 the ability to provide your own AWS KMS key for encryption of files being stored in your S3 bucket. 

Note 

If web connectors are used, a markdown text is passed to Lambda instead of HTML. 

Alternatively, you may want to specify chunk-level metadata, while having the knowledge base apply 
 one of the natively supported chunking strategies. In this case, select one of the pre-defined chunking 
 strategies (for example, default or fixed-size chunking), while providing 
 a reference to your Lambda function and S3 bucket. In this case, the knowledge base will store parsed and 
 pre-chunked files in the pre-defined S3 bucket, before calling your Lambda function for further adding 
 chunk-level metadata. 

After adding chunk-level metadata, your Lambda function will write back chunked files 
 into the same bucket and return references for the knowledge base for further processing. Please note that 
 chunk-level metadata take precedence and overwrite file-level metadata, in case of any collisions. 

For an example of using a Python Lambda function for custom chunking, see Custom chunking using Lambda function . 

For API and file contracts, refer the the below structures: 

API contract when adding a custom transformation using Lambda function 

{ ...
 "vectorIngestionConfiguration": { "customTransformationConfiguration": { // Custom transformation 
 "intermediateStorage": { "s3Location": { // the location where input/output of the Lambda is expected 
 "uri": "string"
 }
 },
 "transformations": [ { "transformationFunction": { "transformationLambdaConfiguration": { "lambdaArn": "string"
 }
 },
 "stepToApply": "string" // enum of POST_CHUNKING
 }]
 },
 "chunkingConfiguration": { "chunkingStrategy": "string",
 "fixedSizeChunkingConfiguration": { "maxTokens": "number",
 "overlapPercentage": "number"
 }
 ...
 }
 }
} 
Custom Lambda transformation input format 

{ "version": "1.0",
 "knowledgeBaseId": "string",
 "dataSourceId": "string",
 "ingestionJobId": "string",
 "bucketName": "string",
 "priorTask": "string",
 "inputFiles": [ { "originalFileLocation": { "type": "S3",
 "s3_location": { "uri": "string"
 }
 },
 "fileMetadata": { "key1": "value1",
 "key2": "value2"
 },
 "contentBatches": [ { "key":"string"
 }]
 }]
} 
Custom Lambda transformation output format 

{ "outputFiles": [ { "originalFileLocation": { "type": "S3",
 "s3_location": { "uri": "string"
 }
 },
 "fileMetadata": { "key1": "value1",
 "key2": "value2"
 },
 "contentBatches": [ { "key": "string"
 }]
 }]
} 
File format for objects in referenced in fileContents 

{ "fileContents": [ { "contentBody": "...",
 "contentType": "string", // enum of TEXT, PDF, ...
 "contentMetadata": { "key1": "value1",
 "key2": "value2"
 }
 }
 ...
 ]
} 

Document Conventions 
Parsing options 
Include metadata in a data source 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
