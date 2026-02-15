# Crawl web pages for your knowledge base - Amazon Bedrock Crawl web pages for your knowledge base - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/webcrawl-data-source-connector.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Crawl web pages for your knowledge base - Amazon Bedrock 
Crawl web pages for your knowledge base - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
Supported features Prerequisites Connection configuration 

Crawl web pages for your knowledge base 

The Amazon Bedrock provided Web Crawler connects to and crawls URLs you have selected for use in your Amazon Bedrock knowledge base. 
 You can crawl website pages in accordance with your set scope or limits for your selected URLs. You can crawl 
 website pages using either the AWS Management Console for Amazon Bedrock or the CreateDataSource API (see Amazon Bedrock supported SDKs and AWS CLI ). Currently, only Amazon OpenSearch Serverless vector store is available to use with this data source. 

Note 

The Web Crawler data source connector is in preview release and is subject to change. 

When selecting websites to crawl, you must adhere to the Amazon Acceptable Use Policy and all other Amazon terms. Remember that you must only use the Web Crawler to 
 index your own web pages, or web pages that you have authorization to crawl and must respect robots.txt configurations.. 

The Web Crawler respects robots.txt in accordance with the RFC 9309 

There are limits to how many web page content items and MB per content item that can be crawled. See Quotas for knowledge bases . 

Topics 

Supported features 

Prerequisites 

Connection configuration 

Supported features 
The Web Crawler connects to and crawls HTML pages starting from the seed URL, traversing all child links under the same 
 top primary domain and path. If any of the HTML pages reference supported documents, the Web Crawler will 
 fetch these documents, regardless if they are within the same top primary domain. You can modify the crawling behavior 
 by changing the crawling configuration - see Connection configuration . 

The following is supported for you to: 

Select multiple source URLs to crawl and set the scope of URLs to crawl only the host or also include subdomains. 

Crawl static web pages that are part of your source URLs. 

Specify custom User Agent suffix to set rules for your own crawler. 

Include or exclude certain URLs that match a filter pattern. 

Respect standard robots.txt directives like 'Allow' and 'Disallow'. 

Limit the scope of the URLs to crawl and optionally exclude URLs that match a
 filter pattern. 

Limit the rate of crawling URLs and the maximum number of pages to
 crawl. 

View the status of crawled URLs in Amazon CloudWatch 

Prerequisites 
To use the Web Crawler, make sure you: . 

Check that you are authorized to crawl your source URLs. 

Check the path to robots.txt corresponding to your source URLs doesn't block
 the URLs from being crawled. The Web Crawler adheres to the standards of
 robots.txt: disallow by default if robots.txt is not found for the
 website. The Web Crawler respects robots.txt in accordance with the RFC 9309 . You can
 also specify custom User Agent header suffix to set rules for your own crawler.
 For more information, see Web Crawler URL access in Connection configuration instructions on this
 page. 

Enable CloudWatch Logs delivery and follow examples of Web Crawler logs to view the status of your data ingestion job for 
 ingesting web content, and if certain URLs cannot be retrieved. 

Note 

When selecting websites to crawl, you must adhere to the Amazon Acceptable Use Policy and all other Amazon terms. Remember that you must only use the Web Crawler to 
 index your own web pages, or web pages that you have authorization to crawl. 

Connection configuration 
For more information about sync scope for crawling URLs, 
 inclusion/exclusion filters, URL access, incremental syncing, and how these work, 
 select the following: 

You can limit the scope of the URLs to crawl based on each page URL's specific relationship to the 
 seed URLs. For faster crawls, you can limit URLs to those with the same host and initial URL path 
 of the seed URL. For more broader crawls, you can choose to crawl URLs with the same host or 
 within any subdomain of the seed URL. 

You can choose from the following options. 

Default: Limit crawling to web pages that belong to the same host and with the 
 same initial URL path. For example, with a seed URL of 
 "https://aws.amazon.com/bedrock/" then only this path and web pages that extend 
 from this path will be crawled, like "https://aws.amazon.com/bedrock/agents/". 
 Sibling URLs like "https://aws.amazon.com/ec2/" are not crawled, for example. 

Host only: Limit crawling to web pages that belong to the same host. For example, with a
 seed URL of "https://aws.amazon.com/bedrock/", then web pages with
 "https://aws.amazon.com" will also be crawled, like
 "https://aws.amazon.com/ec2". 

Subdomains: Include crawling of any web page that has the same primary domain as
 the seed URL. For example, with a seed URL of
 "https://aws.amazon.com/bedrock/" then any web page that
 contains "amazon.com" (subdomain) will be crawled, like "https://www.amazon.com". 

Note 

Make sure you are not crawling potentially excessive web pages. It's not recommended to 
 crawl large websites, such as wikipedia.org, without filters or scope limits. Crawling 
 large websites will take a very long time to crawl. 

Supported file types are crawled regardless of scope and if there's 
 no exclusion pattern for the file type. 

The Web Crawler supports static websites. 

You can also limit the rate of crawling URLs to control the throttling of crawling speed. You 
 set the maximum number of URLs crawled per host per minute. In addition, you can also set the maximum
 number (up to 25,000) of total web pages to crawl. Note that if the total number of web pages from your 
 source URLs exceeds your set maximum, then your data source sync/ingestion job will fail. 

You can include or exclude certain URLs in accordance with your scope. Supported file types are crawled regardless of scope and if there's 
 no exclusion pattern for the file type. If you specify an inclusion and exclusion 
 filter and both match a URL, the exclusion filter takes precedence and the 
 web content isn’t crawled. 

Important 

Problematic regular expression pattern filters that lead to catastrophic backtracking and look ahead are rejected. 

An example of a regular expression filter pattern to exclude URLs that end with ".pdf" or PDF 
 web page attachments: ".*\.pdf$" 

You can use the Web Crawler to crawl the pages of websites that you are authorized to crawl. 

When selecting websites to crawl, you must adhere to the Amazon Acceptable Use Policy and all other Amazon terms. Remember that you must only use the Web Crawler to 
 index your own web pages, or web pages that you have authorization to crawl. 

The Web Crawler respects robots.txt in accordance with the RFC 9309 

You can specify certain user agent bots to either ‘Allow’ or ‘Disallow’ the
 user agent to crawl your source URLs. You can modify the robots.txt file of your
 website to control how the Web Crawler crawls your source URLs. The crawler will
 first look for bedrockbot-UUID rules and then for generic bedrockbot rules in the robots.txt file. 

You can also add a User-Agent suffix that can be used to allowlist your
 crawler in bot protection systems. Note that this suffix does not need to be
 added to the robots.txt file to make sure that no one can impersonate the User
 Agent string. For example, to allow the Web Crawler to crawl all website content
 and disallow crawling for any other robots, use the following directive: 

User-agent: bedrockbot-UUID # Amazon Bedrock Web Crawler
Allow: / # allow access to all pages
User-agent: * # any (other) robot
Disallow: / # disallow access to any pages 

Each time the the Web Crawler runs, it retrieves content for all URLs that are reachable from the source 
 URLs and which match the scope and filters. For incremental syncs after the first sync of all content, Amazon Bedrock will update your 
 knowledge base with new and modified content, and will remove old content that is no longer present. Occasionally, the 
 crawler may not be able to tell if content was removed from the website; and in this case it will err on the side 
 of preserving old content in your knowledge base. 

To sync your data source with your knowledge base, use the StartIngestionJob API or select your knowledge 
 base in the console and select Sync within the data source overview section. 

Important 

All data that you sync from your data source becomes available to anyone with bedrock:Retrieve permissions to retrieve the data. This can also include any data with controlled 
 data source permissions. For more 
 information, see Knowledge base permissions . 

Console 
Connect a Web Crawler data source to your knowledge base 

Follow the steps at Create a knowledge base by connecting to a data source in Amazon Bedrock Knowledge Bases and choose Web Crawler as the data source. 

Provide a name and optional description for the data source. 

Provide the Source URLs of the URLs you want to crawl.
 You can add up to 9 additional URLs by selecting Add Source URLs . By providing a source URL, you are confirming that you are authorized to crawl its domain. 

In the Advanced settings section, you can optionally configure the following: 

KMS key for transient data storage. – You can encrypt the transient data while converting your data into embeddings with the default AWS managed key or your own KMS key. For more information, see Encryption of transient data storage during data ingestion . 

Data deletion policy – You can delete the vector embeddings for your data source that are stored in the vector store by default, or choose to retain the vector store data. 

(Optional) Provide a user agent suffix for bedrock-UUID- that identifies the crawler or bot when it accesses a web server. 

Configure the following in the Sync scope section: 

Select a Website domain range for crawling your source URLs: 

Default: Limit crawling to web pages that belong to the same host and with the 
 same initial URL path. For example, with a seed URL of 
 "https://aws.amazon.com/bedrock/" then only this path and web pages that extend 
 from this path will be crawled, like "https://aws.amazon.com/bedrock/agents/". 
 Sibling URLs like "https://aws.amazon.com/ec2/" are not crawled, for example. 

Host only: Limit crawling to web pages that belong to the same host. For example, with a
 seed URL of "https://aws.amazon.com/bedrock/", then web pages with
 "https://aws.amazon.com" will also be crawled, like
 "https://aws.amazon.com/ec2". 

Subdomains: Include crawling of any web page that has the same primary domain as
 the seed URL. For example, with a seed URL of
 "https://aws.amazon.com/bedrock/" then any web page that
 contains "amazon.com" (subdomain) will be crawled, like "https://www.amazon.com". 

Note 

Make sure you are not crawling potentially excessive web pages. It's not recommended to 
 crawl large websites, such as wikipedia.org, without filters or scope limits. Crawling 
 large websites will take a very long time to crawl. 

Supported file types are crawled regardless of scope and if there's 
 no exclusion pattern for the file type. 

Enter Maximum throttling of crawling speed . Ingest URLs between 1 and 300 URLs per host per minute. A higher crawling speed increases the load but takes less time. 

Enter Maximum pages for data source sync between 1 and 25000. Limit the maximum number of web pages crawled from your source URLs. If web pages exceed this number the data source sync will fail and no web pages will be ingested. 

For URL Regex patterns (optional) you can add Include patterns or Exclude patterns by entering the regular expression pattern in the box.
 You can add up to 25 include and 25 exclude filter patterns by selecting Add new pattern . 
 The include and exclude patterns are crawled in accordance with your scope. 
 If there's a conflict, the exclude pattern takes precedence. 

(Optional) In the Content parsing and chunking section, you can customize how to parse and chunk your data. Refer to the following resources to learn more about these customizations: 

For more information about parsing options, see Parsing options for your data source . 

For more information about chunking strategies, see How content chunking works for knowledge bases . 

Warning 

You can't change the chunking strategy after connecting to the data source. 

For more information about how to customize chunking of your data and processing of your metadata with a Lambda function, see Use a custom transformation Lambda function to define how your data is ingested . 

Continue to choose an embeddings model and vector store. To see the remaining steps, return to Create a knowledge base by connecting to a data source in Amazon Bedrock Knowledge Bases and continue from the step after connecting your data source. 

API 
To connect a knowledge base to a data source using WebCrawler, send a CreateDataSource request with an Agents for Amazon Bedrock build-time endpoint , specify WEB in the type field of the DataSourceConfiguration , and include the webConfiguration field. The following is an example of a configuration of Web Crawler for your Amazon Bedrock 
 knowledge base. 

{ "webConfiguration": { "sourceConfiguration": { "urlConfiguration": { "seedUrls": [ { "url": "https://www.examplesite.com"
 }]
 }
 },
 "crawlerConfiguration": { "crawlerLimits": { "rateLimit": 50,
 "maxPages": 100
 },
 "scope": "HOST_ONLY",
 "inclusionFilters": [
 "https://www\.examplesite\.com/.*\.html"
 ],
 "exclusionFilters": [
 "https://www\.examplesite\.com/contact-us\.html"
 ],
 "userAgent": "CustomUserAgent"
 }
 },
 "type": "WEB"
} 
To learn about customizations that you can apply to ingestion by including the optional vectorIngestionConfiguration field, see Customize ingestion for a data source . 

Document Conventions 
Salesforce 
Custom 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
