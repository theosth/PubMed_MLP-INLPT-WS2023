# Meetingnotes 23.10.2023

## Participants
* [X] Lukas
* [X] Benedikt
* [X] Theo
* [X] Dominik

## Topics
* Discuss which data set to use -> PubMed dataset
* Plan recurring meetings for the next weeks
    * -> every Monday 16:00 to 17:45
* Discuss how to proceed with the project
* Decision to look into opensearch
* first talk about frontend decisions
* create Discord server for communication


## Open Tasks
* [ ] Explore PubMed dataset
* [ ] Look into how to scrape the data set (look into the API)
* [ ] Look into different options to store the data
* [ ] Look into opensearch
* [ ] Analyze data set
* [ ] Maybe already look into pre-trained models, which could be used for the project (Should we do this already? Maybe it will be more efficient later because it gets introduced in the lecture)
* [ ] Look into simple first frontend implementation



# Meetingnotes 26.10.2023

## Participants
* [X] Lukas
* [X] Benedikt
* [X] Theo
* [X] Dominik

## Topics
* Explore PubMed API using Python library
* Explore OpenSearch capabilities for finding relevant documents for a search query
and analysis of text data (topic recognition etc.). 
=> can integrate word embedding model to find semantic similarities
* Experiment with Google Colab and Github and integrating them into our dev process. 


# Meetingnotes 13.11.2023

## Participants
* [X] Lukas
* [X] Benedikt
* [X] Theo
* [X] Dominik

## Topics
* Discuss and decide on openSearch for data storage, further work on including data into openSearch
* Look into further vector features of openSearch (that were not discussed in the tutorial)
* Show progress with streamlit, decision to try further stuff (frontend) with streamlit

## Open Tasks
See above


# Meetingnotes 15.11.2023
## Participants
* [X] Lukas
* [X] Benedikt
* [X] Theo
* [X] Dominik

## Topics
* Quick meeting planning prior to the meeting with our supervisor tomorrow
* Discuss current progress and next steps

## Closed Tasks
* [ ] writing a scraper and scraping the dataset
* [ ] frontend implementation with streamlit
* [ ] setup project structure and api (with FastAPI) for the backend (that later hosts the model)

## Open Tasks
* next steps will be filled after the meeting with our supervisor


# Meetingnotes 16.11.2023 - Meeting with Supervisor
## Participants
* [X] Lukas
* [X] Benedikt
* [X] Theo
* [X] Dominik
* [X] Ashish

## Topics
* Discuss current progress and next steps
* Look at MoSCoW and discuss which features are mandatory, optional, should have and could have
* --> Team needs to further specify the features and the scope of the project. Especially functional requirements regarding types of questions the system should be able to answer.
* Talk about OpenSearch and further steps of storing the data -> include a vector field for now and rather over-collect the metadata instead of not including it
* maybe research vector-databases -> embeddings will later be discussed in the lect. delay that part until we know more about it
* talk our current workflow pipeline ideas and first implementations that can the be later improved upon


# Meetingnotes 27.11.2023

## Participants
* [X] Lukas
* [X] Benedikt
* [X] Theo
* [X] Dominik

## Topics

* Discussion of results of the investigation of OpenSearch as database. 
* Discussion of Search/Embedding Method to use.
    * Consultation by Dr. Prof. Gertz
* Discussion of project strategy:
    * Create High level plan
    * Document ideas and discussions regarding selected tech



# Meetingnotes 18.12.2023

## Participants
* [X] Lukas
* [X] Benedikt
* [X] Theo
* [X] Dominik

## Topics

* Discussion of next steps
    * Retrieval-System:
        1) Fill in database (Script)
        2) Token-Splitting (~ 3 Documents per Abstract, overlapping documents; use same Tokenizer, write explanation on why this splitting)
        3) Embedding-Model for Splits (BM25, pritamdeka/S-PubMedBert-MS-MARCO, 3. model?)
        4) Retrieval-Testset (Question should refer to document (not abstract); Yes/No and factual questions; Create questions using ChatGPT, test set should be used to evaluate embedding model and different search types)
        5) experiments for search (k-Nearest-Neighbors for Embeddings (PubMedBert), syntactical search (BM25), Hybrid with metadata (Keywords, title, etcare syntactical (BM25) content semantical (PubMedBert)); use different searches, same Splitting), try out different hybrid strategies
        6) make some tests for different hybrid strategies and/or do some research on best practices/variants that have proven to be good
    * QA-System (Extractive), probably just use existing model, no finetuning? -> At least not in the next steps, Requirements for the model:
        1) Yes/No and factual questions should be answered by same model (mandatory)
        2) Input of model is text (mandatory)
        3) Should support PubMed vocabulary (optional)
        4) Should support large inputs (optional) -> Input size of most models should be enough

* What do we want to do until the milestone?
    * Mostly finish retrieval-system, maybe start some research for QA-Model
    * Test different variations of retrieval system and decide on which parts we use

# Meetingnotes 09.02.2023

## Participants
* [X] Lukas
* [X] Benedikt
* [X] Theo
* [X] Dominik

## Topics

* Architecture decisions
    * Retrieval-System:
        * Consideration of using a different database instead of OpenSearch (maybe Pinecone)
        * Talk about how to evaluate it
        * discuss several further refinements of the retrieval steps that could potentially increase the performance of the retrieval system (like question enrichment, query transformation etc.)
    * Answer-System:
        * how to support the different question types
            * were to focus on in evaluation
            * how to automate the evaluation to get better overall results 
            * discuss our focus on yes/no and potentially factual question for the main part of the anwer system. Idea to rather focus on one part and do it very well than doing everything a bit. (yes/no and factual can be evaluated the best -> then also on more test pairs)

* Discussion of how we will organize the final phase of our project
    * discuss further meetings
    * discuss internal deadlines for the next steps
    * distribute work among the team members

# Meeting Notes 20.02.-01.03

For this time frame we do not have separate Meeting Notes because some of the group 
members were meeting nearly every other day to work on the project separately or 
collaboratively. For instance, we met at Theo's on Wednesday 28.02. and Friday 01.03. 
and spent the whole day working in the same room and discussing things whenever 
something came up. For instance, we discussed what other features we could implement 
and get to work in the time. We discussed what other retrieval and generation 
strategies (like self-querying) we could use and so on. All in all, the collaboration 
was very smooth and productive