# View information about an Amazon Bedrock knowledge base - Amazon Bedrock View information about an Amazon Bedrock knowledge base - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-info.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

View information about an Amazon Bedrock knowledge base - Amazon Bedrock 
View information about an Amazon Bedrock knowledge base - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 

View information about an Amazon Bedrock knowledge base 

You can view information about a knowledge base, such as the settings and status. 

To monitor your knowledge base using Amazon CloudWatch logs, see Knowledge base logging . 

Choose the tab for your preferred method, and then follow the steps: 
Console 
To view information about a knowledge base 

Sign in to the AWS Management Console with an IAM identity that has permissions to use the Amazon Bedrock console. Then, open the Amazon Bedrock console at https://console.aws.amazon.com/bedrock . 

In the left navigation pane, choose Knowledge bases . 

To view details for a knowledge base, either select the Name of the source or choose the radio button next to the source and select Edit . 

On the details page, you can carry out the following actions: 

To change the details of the knowledge base, select Edit in the Knowledge base overview section. 

To update the tags attached to the knowledge base, select Manage tags in the Tags section. 

If you update the data source from which the knowledge base was created and need to sync the changes, select Sync in the Data source section. 

To view the details of a data source, select a Data source name . Within the details, you can choose the radio button next to a sync event in the Sync history section and select View warnings to see why files in the data ingestion job failed to sync. 

To manage the vector embeddings model used for the knowledge base, select Edit Provisioned Throughput . 

Select Save changes when you are finished editing. 

API 
To get information about a knowledge base, send a GetKnowledgeBase request with a Agents for Amazon Bedrock build-time endpoint , specifying the knowledgeBaseId . 

To list information about your knowledge bases, send a ListKnowledgeBases request with a Agents for Amazon Bedrock build-time endpoint . You can set the maximum number of results to return in a response. If there are more results than the number you set, the response returns a nextToken . You can use this value in the nextToken field of another ListKnowledgeBases request to see the next batch of results. 

Document Conventions 
Deploy your knowledge base for your application 
Modify a knowledge base 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
