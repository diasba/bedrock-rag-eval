# Prompt templates and examples for Amazon Bedrock text models - Amazon Bedrock Prompt templates and examples for Amazon Bedrock text models - Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-templates-and-examples.html
Fetched-At: 2026-02-15T17:09:14.863044+00:00

---

Prompt templates and examples for Amazon Bedrock text models - Amazon Bedrock 
Prompt templates and examples for Amazon Bedrock text models - Amazon Bedrock 
Documentation Amazon Bedrock User Guide 
Text classification Question-answer, without context Question-answer, with context Summarization Text generation Code generation Mathematics Reasoning/logical thinking Entity extraction Chain-of-thought reasoning 

Prompt templates and examples for
 Amazon Bedrock text models 

Common tasks supported by LLMs on Amazon Bedrock include text classification,
 summarization, and questions and answers (with and without context). For these tasks,
 you can use the following templates and examples to help you create prompts for Amazon Bedrock
 text models. 

Topics 

Text classification 

Question-answer, without context 

Question-answer, with context 

Summarization 

Text generation 

Code generation 

Mathematics 

Reasoning/logical thinking 

Entity extraction 

Chain-of-thought reasoning 

Text classification 
For text classification, the prompt includes a question with several possible
 choices for the answer, and the model must respond with the correct choice. Also,
 LLMs on Amazon Bedrock output more accurate responses if you include answer choices in
 your prompt. 

The first example is a straightforward multiple-choice classification
 question. 

Prompt template for Titan """ { { Text}} { { Question}}? Choose from the following: { { Choice 1}} { { Choice 2}} { { Choice 3}}""" 

User prompt: San Francisco, officially the City and County 
of San Francisco, is the commercial, financial, and cultural 
center of Northern California. The city proper is the fourth 
most populous city in California, with 808,437 residents, 
and the 17th most populous city in the United States as of 2022.

What is the paragraph above about? Choose from the following:

A city
A person
An event 

Output: A city 

(Source of prompt: Wikipedia on San Francisco , model used: Amazon Titan Text) 

Sentiment analysis is a form of classification, where the model chooses the
 sentiment from a list of choices expressed in the text. 

Prompt template for Titan: """The following is text from a { { Text Type, e.g. “restaurant 
review”}} { { Input}}
Tell me the sentiment of the { { Text Type}} and categorize it 
as one of the following: { { Sentiment A}} { { Sentiment B}} { { Sentiment C}}""" 

User prompt: The following is text from a restaurant review:

“I finally got to check out Alessandro’s Brilliant Pizza 
and it is now one of my favorite restaurants in Seattle. 
The dining room has a beautiful view over the Puget Sound 
but it was surprisingly not crowed. I ordered the fried 
castelvetrano olives, a spicy Neapolitan-style pizza 
and a gnocchi dish. The olives were absolutely decadent, 
and the pizza came with a smoked mozzarella, which 
was delicious. The gnocchi was fresh and wonderful. 
The waitstaff were attentive, and overall the experience 
was lovely. I hope to return soon.”

Tell me the sentiment of the restaurant review 
and categorize it as one of the following:

Positive
Negative
Neutral 

Output: Positive. 

(Source of prompt: AWS, model used: Amazon Titan Text) 

The following example uses Anthropic Claude models to classify text. As
 suggested in AnthropicClaude Guides , use XML tags such as <text></text> to denote
 important parts of the prompt. Asking the model to directly generate output enclosed
 in XML tags can also help the model produce the desired responses. 

Prompt template for Anthropic Claude: """
 
 
Human: { { classification task description}}
<text> { { input text content to be classified}}
</text>

Categories are: { { category name 1}} { { category name 2}} { { category name 3}}

Assistant:""" (Source: Written by AWS) 

User prompt: Human: Classify the given product description into given 
categories. Please output the category label in 
<output></output> tags.

Here is the product description.

<text>
Safe, made from child-friendly materials with smooth edges.
Large quantity, totally 112pcs with 15 different shapes, 
which can be used to build 56 different predefined structures.
Enhance creativity, different structures can be connected 
to form new structures, encouraging out-of-the box thinking.
Enhance child-parent bonding, parents can play with their 
children together to foster social skills.
</text>

Categories are:
(1) Toys
(2) Beauty and Health
(3) Electronics

Assistant: 

Output: <output>Toys</output> 

(Source of prompt: AWS, model used: Anthropic
 Claude) 

Question-answer, without context 
In a question-answer prompt without context, the model must answer the question
 with its internal knowledge without using any context or document. 

Prompt Template to Titan """ { { Question}}""" 

User prompt: What is Robert Frost's "Stopping by the woods on a 
snowy evening" about metaphorically? 

Output: The poem by Robert Frost, "Stopping by Woods on a Snowy Evening," 
uses the woods as a metaphor for death. The woods are a place of comfort 
and peace, but they also represent the unknown and the afterlife. 
The poem suggests that death is not something to be feared, 
but rather a natural part of life that we should all embrace.

The poem begins with the speaker stopping by the woods on a snowy evening, 
a moment of contemplation and reflection. The speaker notices the beauty 
of the snow-covered woods and is reminded of the fleeting nature of life. 
The poem continues as the speaker considers the temptation of continuing 
on to his destination, but instead chooses to pause and take in the beauty 
of the woods.

The woods are used as a metaphor for the unknown and the afterlife. 
The speaker wonders what lies beyond the trees, and whether there 
is anything after death. The poem suggests that death is not 
something to be feared, but rather a natural part of life 
that we should all embrace.

The final lines of the poem are perhaps the most famous and poignant: 
"And miles to go before I sleep, and miles to go before I sleep." 
These lines suggest that even though the speaker has paused 
to appreciate the beauty of the woods, they still have a 
long journey ahead of them. The poem is a reminder that life 
is fleeting, and that we should take the time to appreciate 
the beauty around us, even as we work towards our goals and ambitions.

Overall, "Stopping by Woods on a Snowy Evening" is a beautiful 
and thought-provoking poem that uses the metaphor of the woods 
to explore the concept of death and the afterlife. 

(Source of prompt: AWS, model used: Amazon Titan Text) 

Model
 encouragement can also help in question-answer tasks. 

Prompt Template to Titan """ { { Model encouragement}} { { Question}}""" 

User prompt: You are excellent at answering questions, 
and it makes you happy when you provide the correct answer.

What moon in the solar system is most likely to host life? 

Output: The moon of Titan, which is a moon of the planet Saturn, 
is the most likely to support life in the solar system.

Titan is the only known moon in the solar system to have a dense 
atmosphere and a liquid hydrosphere, and scientists believe that 
it may contain the chemical building blocks for life. 
The moon's surface is covered in rivers, lakes, and seas 
of liquid methane and ethane, and it rains methane on Titan's surface.

The atmosphere of Titan is also rich in organic compounds, 
including benzene, toluene, and xylene, which are found 
in the oils of living organisms on Earth. 
Additionally, Titan has a magnetic field and a tenuous atmosphere, 
which could provide protection from harmful radiation and 
help maintain a stable climate.

While there is no direct evidence of life on Titan, 
scientists believe that it is one of the most promising 
places in the solar system to search for life beyond Earth. 

(Source of prompt: AWS, model used: Amazon Titan Text) 

Prompt template to Titan """ { { Model encouragement}} { { Question}} { { Constraints}}""" 

User prompt: You feel rewarded by helping people learn more about climate change.
Could you please explain what climate change is?
Assume your audience is composed of high school students. 

Output: Climate change is the long-term warming of the planet, 
which can be caused by human activities such as burning fossil fuels 
and deforestation, as well as natural processes. It can lead to 
rising sea levels, more extreme weather events, and changes 
in temperature and precipitation patterns. 

(Source of prompt: AWS, model used: AI21 Labs Jurassic-2 Ultra v1) 

Question-answer, with context 
In a question-answer prompt with context, an input text followed by a question is
 provided by the user, and the model must answer the question based on information
 provided within the input text. Putting the question in the end after the text can
 help LLMs on Amazon Bedrock better answer the question.
 Model
 encouragement works for this use case as well. 

Prompt template to Titan """ { { Text}} { { Question}}""" 

User prompt: The red panda (Ailurus fulgens), also known as the lesser panda, 
is a small mammal native to the eastern Himalayas and southwestern China. 
It has dense reddish-brown fur with a black belly and legs, white-lined ears, 
a mostly white muzzle and a ringed tail. Its head-to-body length is 51–63.5 cm 
(20.1–25.0 in) with a 28–48.5 cm (11.0–19.1 in) tail, and it weighs between 
3.2 and 15 kg (7.1 and 33.1 lb). It is well adapted to climbing due to its 
flexible joints and curved semi-retractile claws.

The red panda was first formally described in 1825. The two currently 
recognized subspecies, the Himalayan and the Chinese red panda, genetically 
diverged about 250,000 years ago. The red panda's place on the evolutionary 
tree has been debated, but modern genetic evidence places it in close 
affinity with raccoons, weasels, and skunks. It is not closely related 
to the giant panda, which is a bear, though both possess elongated 
wrist bones or "false thumbs" used for grasping bamboo. 
The evolutionary lineage of the red panda (Ailuridae) stretches 
back around 25 to 18 million years ago, as indicated by extinct 
fossil relatives found in Eurasia and North America.

The red panda inhabits coniferous forests as well as temperate broadleaf 
and mixed forests, favoring steep slopes with dense bamboo cover close 
to water sources. It is solitary and largely arboreal. It feeds mainly 
on bamboo shoots and leaves, but also on fruits and blossoms. 
Red pandas mate in early spring, with the females giving birth 
to litters of up to four cubs in summer. It is threatened 
by poaching as well as destruction and fragmentation of habitat 
due to deforestation. The species has been listed as Endangered 
on the IUCN Red List since 2015. It is protected in all range countries.

Based on the information above, what species are red pandas closely related to? 

Output: Red pandas are closely related to raccoons, weasels, and skunks. 

(Source of prompt: https://en.wikipedia.org/wiki/Red_panda, model used: Amazon
 Titan Text) 

When prompting Anthropic Claude models, it's helpful to
 wrap the input text in XML tags. In the following example, the input text is
 enclosed in <text></text> . 

Prompt template for Anthropic Claude: """

Human: { { Instruction}}
<text> { { Text}}
<text> { { Question}}

Assistant:""" 

User prompt: Human: Read the following text inside <text></text> 
XML tags, and then answer the question:

<text>
On November 12, 2020, the selection of the Weeknd to headline 
the show was announced; marking the first time a Canadian solo artist 
headlined the Super Bowl halftime show. When asked about preparations 
for the show, the Weeknd stated, "We've been really focusing 
on dialing in on the fans at home and making performances 
a cinematic experience, and we want to do that with the Super Bowl." 

The performance featured a choir whose members were dressed in white 
and wore masks over their faces with glowing red eyes, and were 
standing within a backdrop of a neon cityscape. The performance 
opened with a white figure dressed the same as the choir being 
lowered into the backdrop where the choir was standing while singing 
“Call Out My Name". At this time, the Weeknd sat in a convertible 
against a skyline backdrop designed to resemble the Las Vegas Strip. 
For the next part of the performance, the backdrop then split open 
to reveal the Weeknd, who then performed "Starboy", followed by "The Hills". 

Next, performing the song "Can't Feel My Face", the Weeknd traveled 
through a labyrinth constructed behind the stage, joined by dancers 
dressed in red blazers and black neckties similar to his, 
but with their faces covered with bandages, in keeping with 
the aesthetic of his fourth studio album After Hours (2020). 
The dancers would wear these bandages throughout the performance. 
In the labyrinth section of the performance, camerawork was visually unsteady. 
The next songs performed were "I Feel It Coming", "Save Your Tears", 
and "Earned It". For the "Earned It" performance, the Weeknd 
was accompanied by violinists. For the finale of the show, 
the Weeknd took to the field of the stadium with his dancers to perform 
“Blinding Lights". He and the dancers entered the field by performing 
"House of Balloons / Glass Table Girls". The performance ended 
with an array of fireworks.
</text>
Based on the text above, what songs did the Weeknd play 
at the Super Bowl halftime show?

Assistant: 

Output: Based on the text, the songs the Weeknd played 
at the Super Bowl halftime show were:

- Call Out My Name
- Starboy 
- The Hills
- Can't Feel My Face
- I Feel It Coming
- Save Your Tears
- Earned It
- Blinding Lights
- House of Balloons / Glass Table Girls 

(Source of prompt: Wikipedia on
 the Super Bowl LV halftime show , model used:
 Anthropic Claude) 

Summarization 
For a summarization task, the prompt is a passage of text, and the model must
 respond with a shorter passage that captures the main points of the input.
 Specification of the output in terms of length (number of sentences or paragraphs)
 is helpful for this use case. 

Prompt template for Titan """The following is text from a { { Text Category}}: { { Text}}
Summarize the { { Text Category}} in { { length of summary, 
e.g., “one sentence” or “one paragraph”}}""" 

User prompt: The following is text from a restaurant review:
“I finally got to check out Alessandro’s Brilliant Pizza 
and it is now one of my favorite restaurants in Seattle. 
The dining room has a beautiful view over the Puget Sound 
but it was surprisingly not crowed. I ordered the fried 
castelvetrano olives, a spicy Neapolitan-style pizza 
and a gnocchi dish. The olives were absolutely decadent, 
and the pizza came with a smoked mozzarella, which was delicious. 
The gnocchi was fresh and wonderful. The waitstaff were attentive, 
and overall the experience was lovely. I hope to return soon.”
Summarize the above restaurant review in one sentence. 

Output: Alessandro’s Brilliant Pizza is a fantastic restaurant 
in Seattle with a beautiful view over Puget Sound that offers 
decadent and delicious food. 

(Source of prompt: AWS, model used: Amazon Titan Text) 

In the following example, Anthropic Claude summarizes
 the given text in one sentence. To include input text in your prompts, format the
 text with XML mark up: <text> { { text content}} </text> .
 Using XML within prompts is a common practice when prompting
 Anthropic Claude models. 

Prompt template for Anthropic Claude: """

Human: Please read the text:
<text> { { text context}}
</text>

Summarize the text in { { length of summary, e.g., “one 
sentence” or “one paragraph”}}

Assistant:""" 

User prompt: Human: Please read the text:

<text>
In game theory, the Nash equilibrium, named after the mathematician 
John Nash, is the most common way to define the solution 
of a non-cooperative game involving two or more players. 
In a Nash equilibrium, each player is assumed to know 
the equilibrium strategies of the other players, 
and no one has anything to gain by changing only one's own strategy. 
The principle of Nash equilibrium dates back to the time of Cournot, 
who in 1838 applied it to competing firms choosing outputs.
</text>

Summarize the text in one sentence.

Assistant: 

Output: The Nash equilibrium is a concept in game theory 
where each player has adopted a strategy that they have no incentive 
to deviate from given the other players' strategies. 

(Source of prompt: Wikipedia on Nash equilibrium , model used:
 Anthropic Claude) 

Text generation 
Given a prompt, LLMs on Amazon Bedrock can respond with a passage of original text that
 matches the description. Here is one example: 

Prompt template for Titan """Please write a { { Text Category}} in the voice of { { Role}}.""" 

User prompt: Please write an email in the voice of a friend 
congratulating someone on a new job. 

Output: Hey [Name],

I just found out about your new job, and I'm so happy for you! 
Congratulations! You deserve this opportunity since you worked so hard 
to get it. I know you'll do great and make a positive impact on your team. 
I'm here to support you every step of the way. Wishing you all the best 
in this exciting new chapter of your life!

Cheers,
[Your Name] 

(Source of prompt: AWS, model used: Amazon Titan Text) 

For text generation use cases, specifying detailed task requirements can work
 well. In the following example, we ask the model to generate response with
 exclamation points. 

Prompt template for Titan """ { { Task specification}}
Please write a { { Text Category}} in the voice of { { Role}}.""" 

User prompt: Write text with exclamation points.
Please write a formatted email in the voice of a friend 
congratulating someone on a new job. 

Output: Hey [name]!

I just saw the news and I am so, so happy for you! 
You deserve this position and this company with all your heart. 
I can't wait to see you soar and accomplish all the things 
you've been working towards. If anyone is deserving 
of a promotion, it's you!

Congratulations again, friend!

Love,
[name] 

(Source of prompt: AWS, model used: Amazon Titan Text) 

In the following example, a user prompts the model to take on the role of a
 specific person when generating the text. Notice how the signature reflects the role
 the model is taking on in the response. 

Prompt template for Titan """ { { Role assumption}} { { Task description}}
""" 

User input: My name is Jack. Help me write a note expressing my gratitude 
to my parents for taking my son (their grandson) to the zoo. 
I miss my parents so much. 

Output: Dear Mom and Dad,

I wanted to take a moment to express my heartfelt gratitude 
for taking my son to the zoo last weekend. It meant so much to me 
that you took the time to make memories with him, and I am so grateful 
for the love and support you have shown him.

I miss you both so much, and I wish we could be together more often. 
But I know that you will always be there for me and my family, 
and I am so grateful to have you as my parents.

Love,
Jack 

(Source of prompt: AWS, model used: AI21 Labs Jurassic-2 Ultra v1) 

Code generation 
The prompt describes the task or function and programming language for the code
 the user expects the model to generate. 

Prompt template for Titan """Write a function in { { programming language}} to { { task or purpose}}""". 

User input: Write a python function to download a s3 file to local disk. 

Output: The following code can be used to download an s3 file to the local disk.

```Python
import boto3
# Creates a boto3 client object
s3 = boto3.client('s3')
def download_file(bucket_name, object_key, file_path):
try:
# Downloads the s3 file to the specified file path
s3.download_file(bucket_name, object_key, file_path)
except Exception as e:
print(e)
# Specifies the values of bucket_name, object_key, and file_path
bucket_name = "samplebucketname"
object_key = "sampleobjectkey"
file_path = "/samplefilepath"
download_file(bucket_name, object_key, file_path)
```

The given code uses the download_file function to download an s3 file 
to the local disk. The download_file function takes the bucket name, 
object key, and file path as input parameters. The bucket name 
is the name of the s3 bucket where the file is located, 
the object key is the unique identifier of the file within the bucket, 
and the file path is the destination path on the local disk 
where the file will be downloaded. The function uses the download_file method 
of the s3 client to download the file from the specified bucket 
and write it to the specified file path. 

(Source of prompt: AWS, model used: Amazon Titan Text) 

Prompt template for Anthropic Claude """

Human: Write a function in { { programming language}} to { { task or purpose}}

Assistant:""" 

User prompt: Human: Write some python code that quickly approximates 
the square root of a number.

Assistant: 

Output: Here is a simple function to approximate 
the square root of a number using Newton's method:

```python
def sqrt(n, iterations=10):
x = n
for i in range(iterations):
x = (x + n/x) / 2
return x
```

To use it:

```python
print(sqrt(25))
# 5.0

print(sqrt(15, iterations=20)) 
# 3.872983346207417
```

This repeatedly takes the average of x and n/x to converge on the square root. 
More iterations produce a more accurate approximation.

The advantage of this approach is it converges very quickly, 
so even just 10 iterations produces a decent estimate. 

(Source of prompt: AWS, model used: Anthropic
 Claude) 

Mathematics 
The input describes a problem that requires mathematical reasoning at some level,
 which may be numerical, logical,
 geometric,
 or otherwise. For such problem, it's helpful to ask the model to work through the
 problem in a piecemeal manner by adding phrases to instructions such as Let’s
 think step by step or Think step by step to come up with the right
 answer. 

Prompt template for Titan """ { { Math problem description}}
Let’s think step by step.""" 

User prompt: A triangle has two angles of 70 degrees and 50 degrees. 
What is the third angle in degrees?
Let’s think step by step. 

Output: The sum of the three angles in a triangle is always 180 degrees. 
The two given angles are 70 degrees and 50 degrees. 70 + 50 = 120. 
Therefore, the third angle is 180 - 120 = 60 degrees. 
The third angle is 60 degrees. 

(Source of prompt: AWS, model used: Amazon Titan Text) 

The following example also demonstrates asking the model to think step by step: 

Prompt template for Titan """ { { Math problem description}}
Think step by step to come up with the right answer.""" 

User prompt: Lucy has 12 colorful marbles, and she wants to share them 
equally with her 4 friends. How many marbles will each friend receive?
Think step-by-step to come up with the right answer. 

Output: 1. Lucy has 12 marbles and wants to share them equally 
with her 4 friends, then each friend will receive 12 / 4 = 3 marbles.
2. Therefore, each friend will receive 3 marbles. 

(Source of prompt: AWS, model used: AI21 Labs Jurassic-2 Ultra v1) 

Reasoning/logical thinking 
For complex reasoning tasks or problems that requires logical thinking, we can ask
 the model to make logical deductions and explain its answers. 

Prompt template for Titan and AI21 Labs Jurassic: """Question: { { question}} Please output the answer and then explain your answer:""" 

User prompt: Question: Which word is the odd one out? A. accomplished B. good C. horrible D. outstanding Please output the answer and then explain your answer: 

Output: The odd one out is C. horrible. The other three words describe positive qualities or achievements, whereas horrible is an negative adjective. 

(Source of prompt: AWS, model used: Amazon Titan Text) 

Here is another example using the Anthropic Claude
 model: 

Prompt template for Anthropic Claude: """ Human: { { question}} Please provide the answer and show the reasoning. Assistant:""" 

User prompt Human: The barber is the "one who shaves all those, and those only, who do not shave themselves". Does the barber shave himself? Why is this a paradox? Please provide the answer and show the reasoning. Assistant: 

Output: This is an example of a paradox known as the Barber paradox. Here is an explanation: - The statement defines a barber who shaves all and only those people who do not shave themselves. - So if the barber shaves himself, he must shave all those who do not shave themselves, which includes himself. But the barber cannot shave himself as per the initial statement. - If the barber does not shave himself, then he would fit into the group of people who do not shave themselves, and so he must shave himself, according to the statement. But again this contradicts the initial statement. - So the barber cannot shave himself and also cannot not shave himself. This is self-contradictory based on the initial statement about the barber. - Therefore, the statement leads to a paradox where both possibilities (the barber shaving himself or not shaving himself) result in a contradiction. In summary, the paradox arises because the definition of the barber's behavior is self-contradictory when applied to the barber himself. This makes it impossible to determine if the barber shaves himself or not based on the given statement alone. 

(Source of prompt: https://en.wikipedia.org/wiki/Barber_paradox, model used:
 Anthropic Claude) 

Entity extraction 
For entity extraction from a provided input question. Extract entities from
 generated text and place them in XML tags for further processing. 

Prompt template for Titan """You are an expert entity extractor from provided input question. You are responsible for extracting following entities: { { list of entities}}
 
Please follow below instructions while extracting the entity A, and reply in <entityA> </entityA> XML Tags: { { entity A extraction instructions}} 

Please follow below instructions while extracting the entity B, and reply in <entityB> </entityB> XML Tags: { { entity B extraction instructions}} 

Below are some examples: { { some few shot examples showing model extracting entities from give input }} 

(Source of prompt: AWS, model used: Amazon Titan Text G1- Premier) 

Example: 

User: You are an expert entity extractor who extracts entities from provided input question. 
You are responsible for extracting following entities: name, location
Please follow below instructions while extracting the Name, and reply in <name></name> 
XML Tags:

- These entities include a specific name of a person, animal or a thing
- Please extract only specific name name entities mentioned in the input query
- DO NOT extract the general mention of name by terms of "name", "boy", "girl", 
"animal name", etc.

Please follow below instructions while extracting the location, and reply 
in <location></location> XML Tags:
- These entities include a specific location of a place, city, country or a town
- Please extract only specific name location entities mentioned in the input query
- DO NOT extract the general mention of location by terms of "location", "city", "country", 
"town", etc. 

If no name or location is found, please return the same input string as is.

Below are some examples:

input: How was Sarah's birthday party in Seattle, WA?
output: How was <name>Sarah's</name> birthday party 
in <location>Seattle, WA</location>?

input: Why did Joe's father go to the city?
output: Why did <name>Joe's</name> father go to the city?

input: What is the zipcode of Manhattan, New york city?
output: What is the zipcode of <location>Manhattan,New york city<location>?

input: Who is the mayor of San Francisco? 
Bot: 
Chain-of-thought reasoning 
Provide a step-by-step analysis on how the answer was derived. Fact check and
 validate how the model produced an answer. 

Prompt template for Titan """ { { Question}} { { Instructions to Follow }}
Think Step by Step and walk me through your thinking
""" 

(Source of prompt: AWS, model used: Amazon Titan Text G1- Premier) 

Example: 

User: If Jeff had 100 dollars, and he gave $20 to Sarah, 
and bought lottery tickets with another $20. With the lottery 
tickets he bought he won 35 dollars. Jeff then went to buy 
his lunch and spend 40 dollars in lunch. Lastly he made a 
donation to charity for $20. Stephen met with Jeff and wanted 
to lend some money from him for his taxi. How much maximum money 
can Jeff give to Stephen, given that he needs to save $10 for 
his ride back home?. Please do not answer immediately, think 
step by step and show me your thinking.
Bot: 

Document Conventions 
Design a prompt 
Amazon Bedrock Marketplace 

Did this page help you? - Yes 

Thanks for letting us know we're doing a good job! 

If you've got a moment, please tell us what we did right so we can do more of it. 

Did this page help you? - No 

Thanks for letting us know this page needs work. We're sorry we let you down. 

If you've got a moment, please tell us how we can make the documentation better.
