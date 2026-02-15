# How content chunking works for knowledge bases - Amazon Bedrock How content chunking works for knowledge bases - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

How content chunking works for knowledge bases - Amazon Bedrock 
How content chunking works for knowledge bases - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
Standard chunking Hierarchical chunking Semantic chunking Multimodal content chunking 

How content chunking works for knowledge bases 

When ingesting your data, Amazon Bedrock first splits your documents or content into manageable chunks for efficient data 
 retrieval. The chunks are then converted to embeddings and written to a vector index (vector representation 
 of the data), while maintaining a mapping to the original document. The vector embeddings allow the texts to 
 be quantitatively compared. 

Topics 

Standard chunking 

Hierarchical chunking 

Semantic chunking 

Multimodal content chunking 

Standard chunking 
Amazon Bedrock supports the following standard approaches to chunking: 

Note 

Text chunking strategies apply only to text documents. For multimodal content (audio, video, images), chunking occurs at the embedding model level, not through these text-based strategies. 

Fixed-size chunking: You can configure the desired chunk size by specifying the number of tokens per 
 chunk, and an overlap percentage, providing flexibility to align with your specific requirements. You can 
 set the maximum number of tokens that must not exceed for a chunk and the overlap percentage between consecutive 
 chunks. 

Note 

For parsed content (such as content using advanced parsers or converted from HTML), Amazon Bedrock Knowledge Bases 
 may chunk content to optimize for best results. The chunker respects logical document boundaries 
 (such as pages or sections) and does not merge content across these boundaries, even when 
 increasing the maximum token size would otherwise allow for larger chunks. 

Default chunking: Splits content into text chunks of approximately 300 tokens. The chunking process honors 
 sentence boundaries, ensuring that complete sentences are preserved within each chunk. 

You can also choose no chunking for your documents. Each document is treated a single text chunk. You might want 
 to pre-process your documents by splitting them into separate files before choosing no chunking as your chunking 
 approach/strategy. If you choose no chunking for your documents, you cannot view page number in citation or filter by 
 the x-amz-bedrock-kb-document-page-number metadata field/attribute. 

Hierarchical chunking 
Hierarchical chunking involves organizing information into nested structures of child and parent chunks.
 When creating a data source, you are able to define the parent chunk size, child chunk size and the number of 
 tokens overlapping between each chunk. During retrieval, the system initially retrieves child chunks, but replaces 
 them with broader parent chunks so as to provide the model with more comprehensive context. 

Small text embeddings are more precise, but retrieval aims for comprehensive context. A 
 hierarchical chunking system balances these needs by replacing retrieved child chunks with 
 their parent chunks when appropriate. 

Note 

Since child chunks get replaced by parent chunks during retrieval, the returned number of results might be less than the requested amount. 

Hierarchical chunking is not recommended when using S3 vector bucket as your vector store. When using high number of tokens for chunking (over 8000 tokens combined), you may run into metadata size limitations. 

For hierarchical chunking, Amazon Bedrock knowledge bases supports specifying two levels or the following depth for chunking: 

Parent: You set the maximum parent chunk token size. 

Child: You set the maximum child chunk token size. 

You also set the overlap tokens between chunks. This is the absolute number of overlap tokens 
 between consecutive parent chunks and consecutive child chunks. 

Semantic chunking 
Semantic chunking is a natural language processing technique that divides text 
 into meaningful chunks to enhance understanding and information retrieval. It aims to improve 
 retrieval accuracy by focusing on the semantic content rather than just syntactic structure. 
 By doing so, it may facilitate more precise extraction and manipulation of relevant information. 

When configuring semantic chunking, you have the option to specify the following 
 hyper parameters. 

Maximum tokens: The maximum number of tokens that should be included in a single chunk, 
 while honoring sentence boundaries. 

Buffer size: For a given sentence, the buffer size defines the number of surrounding sentences 
 to be added for embeddings creation. For example, a buffer size of 1 results in 3 sentences (current, 
 previous and next sentence) to be combined and embedded. This parameter can influence how much text 
 is examined together to determine the boundaries of each chunk, impacting the granularity and coherence 
 of the resulting chunks. A larger buffer size might capture more context but can also introduce noise, 
 while a smaller buffer size might miss important context but ensures more precise chunking. 

Breakpoint percentile threshold: The percentile threshold of sentence distance/dissimilarity 
 to draw breakpoints between sentences. A higher threshold requires sentences to be more 
 distinguishable in order to be split into different chunks. A higher threshold results in fewer 
 chunks and typically larger average chunk size. 

Note 

There are additional costs to using semantic chunking due to its use of a 
 foundation model. The cost depends on the amount of data you have. See Amazon Bedrock pricing for more 
 information on the cost of foundation models. 

Multimodal content chunking 
For multimodal content (audio, video, images), chunking behavior differs from text documents: 

Nova multimodal embeddings: Chunking occurs at the embedding model level. You can configure audio and video chunk duration from 1-30 seconds (default: 5 seconds). For video files, only the video chunk duration applies, even if the video contains audio. Audio chunk duration only applies to standalone audio files. 

Bedrock Data Automation (BDA) parser: Content is first converted to text (transcripts and scene summaries), then standard text chunking strategies are applied to the converted text. 

Note 

When using Nova multimodal embeddings, the text chunking strategies configured in your knowledge base only affect text documents in your data source, not audio, video, or image files. 

Document Conventions 
Customizing your knowledge base 
Parsing options 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
