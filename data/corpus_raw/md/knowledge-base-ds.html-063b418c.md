# Prerequisites for your Amazon Bedrock knowledge base data - Amazon Bedrock Prerequisites for your Amazon Bedrock knowledge base data - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-ds.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Prerequisites for your Amazon Bedrock knowledge base data - Amazon Bedrock 
Prerequisites for your Amazon Bedrock knowledge base data - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
Supported document formats and
 limits for knowledge base data 

Prerequisites for your Amazon Bedrock knowledge base
 data 

A data source contains files or content with information that can be retrieved when
 your knowledge base is queried. You must store your documents or content in at least one
 of the supported data
 sources . 

Supported document formats and
 limits for knowledge base data 
When you connect to a supported data
 source , the content is ingested into your knowledge base. 

If you use Amazon S3 to store your files or your data source includes attached files,
 then you first must check that each source document file adheres to the
 following: 

The source files are of the following supported formats: 

Format Extension 
Plain text (ASCII only) .txt 
Markdown .md 
HyperText Markup Language .html 
Microsoft Word document .doc/.docx 
Comma-separated values .csv 
Microsoft Excel spreadsheet .xls/.xlsx 
Portable Document Format .pdf 

Each file size doesn't exceed the quota of 50 MB. 

If you use an Amazon S3 or custom data source, you can use multimodal data, including
 JPEG (.jpeg) or PNG (.png) images or files that contain tables, charts,
 diagrams, or other images. 

Note 

The maximum size of .JPEG and .PNG files is 3.75 MB. 

Document Conventions 
Prerequisites 
Prerequisites for using your vector
 store 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
