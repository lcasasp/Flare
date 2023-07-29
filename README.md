# Flare
Flare is an interactive search engine tailored to find and rank current events and news media related to the global climate and energy use crisis. 

Flare will have the search bar users can query to find all current events about climate change and Energy from hundreds if not thousands of news sources and research papers. This would allow the user to perform a search for all news companies, solving the issue of bias previously existing if users searched for topics on a singular news company website. Additionally, this content will be tailored for the climate and energy dual challenge as the data is indexed with Lucene multiple times to best refine the result.

TODO: 
    - Redo scraping, manually search for content only to reduce cost. This means not using news-please library
    - Fix models so they determine whether data is academic or not (bool column). 
    - If academic, use GPT API to summarize academic paper and put into NEW db table.
    - Make a front end page exclusively for our GPT summaries, also add them to general db for querying

    - Make a front end scrollable glove and pin articles by location.

