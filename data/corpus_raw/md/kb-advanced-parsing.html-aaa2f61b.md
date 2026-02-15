# Parsing options for your data source - Amazon Bedrock Parsing options for your data source - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Parsing options for your data source - Amazon Bedrock 
Parsing options for your data source - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

Parsing options for your data source 

Parsing refers to the understanding and extraction of content from raw data. Amazon Bedrock Knowledge Bases offers the following options for parsing your data source during ingestion: 

Amazon Bedrock default parser – Only parses text in text files, including .txt, .md, .html, .doc/.docx, .xls/.xlsx, and .pdf files. This parser doesn't incur any usage charges. 

Note 

Because the default parser only outputs text, we recommend using Amazon Bedrock Data Automation or a foundation model as a parser instead of the default parser if your documents include figures, charts, tables, or images. Amazon Bedrock Data Automation and foundation models can extract these elements from your documents and return them as output. 

Amazon Bedrock Knowledge Bases offers the following parsers to parse multimodal data, including figures, charts, and tables in .pdf files, in addition to .jpeg and .png image files. These parsers can also extract these figures, charts, tables, and images and store them as files in an S3 destination that you specify during knowledge base creation. During knowledge base retrieval, these files can be returned in the response or in source attribution. 

Amazon Bedrock Data Automation – A fully-managed service that effectively processes multimodal data, without the need to provide any additional prompting. The cost of this parser depends on the number of pages in the document or number of images to be processed. For more information about this service, see Amazon Bedrock Data Automation . 

Foundation models – Processes multimodal data using a foundation model. This parser provides you the option to customize the default prompt used for data extraction. The cost of this parser depends on the number of input and output tokens processed by the foundation model. For a list of models that support parsing of Amazon Bedrock Knowledge Bases data, see Supported models and Regions for parsing . 

Important 

If you choose Amazon Bedrock Data Automation or foundation models as a parser, the method that you choose will be used to parse all .pdf files in your data source, even if the .pdf files contain only text. The default parser won’t be used to parse these .pdf files. Your account incurs charges for the use of Amazon Bedrock Data Automation or the foundation model in parsing these files. 

When selecting how to parse your data, consider the following: 

Whether your data is purely textual or if it contains multimodal data, such as images, graphs, and charts, that you want the knowledge base to be able to query. 

Whether you want the option to customize the prompt that is used to instruct the model on how to parse your data. 

The cost of the parser. Amazon Bedrock Data Automation uses per-page pricing, while foundation model parsers charge based on input and output tokens. For more information, see Amazon Bedrock Pricing . 

The total file size limit. When you use foundation models as your parser, the total file size across all files must not be greater than
 100 GB. 

To learn how to configure how your knowledge base is parsed, see the connection configuration for your data source in Connect a data source to your knowledge base . 

Document Conventions 
Content chunking 
Use a Lambda function for data ingestion 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
