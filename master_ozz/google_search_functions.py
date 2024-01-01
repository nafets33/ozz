from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

# importing the environment variables
load_dotenv('.env')
serp_api_key = os.environ.get('serp_api_key')

# Search Functions 

# Text Search
def GoogleTextSearch(query : str) -> list:
    """ This function will take query as an input and 
        will use serpapi to fetch query response and 
        return list
    """

    params = {
        "engine": "google",
        "q": query,
        "api_key": serp_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Extract the Text Results in a list
    textResults = results["organic_results"]

    # Return top 3 search results response from list of all results
    return textResults[:3]



# Image Search
def GoogleImageSearch(query : str) -> list:
    """ This function will take query as an input and 
        will use serpapi to fetch image response and 
        return list of images
    """

    params = {
        "engine": "google_images",
        "q": query,
        "location": "Austin, TX, Texas, United States",  # Change location according the the preference
        "api_key": serp_api_key
    }

    searchForImage = GoogleSearch(params)
    searchResults = searchForImage.get_json()

    # Extract and return thumbnail URLs in a list
    thumbnailURLS = [result.get('thumbnail') for result in searchResults.get('images_results', [])]

    # Return top 3 image URL response from list of thumbnail URLs
    return thumbnailURLS[:3]



# Shopping Search
def GoogleShoppingSearch(query : str) -> list:
    """ This function will take query as an input and 
        will use serpapi to fetch query response and 
        return list of shopping items
    """

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": serp_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    shoppingResults = results["shopping_results"]

    # Return top 3 shopping response from list
    return shoppingResults[:3]



# News Search
def GoogleNewsSearch(query : str) -> list:
    """ This function will take query as an input and 
        will use serpapi to fetch query response and 
        return list of News
    """

    params = {
        "engine": "google_news",
        "q": query,
        "api_key": serp_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    newsResults = results["news_results"]

    # Return top 3 shopping response from list
    return newsResults[:3]



# Maps Search
def GoogleMapsSearch(query : str, location : str) -> list:
    """ This function will take query as an input, location and 
        will use serpapi to fetch query response and 
        return list of Maps
    """

    params = {
        "engine": "google_local",
        "q": query,
        "location": location,   # Provide Location in this format : New+York,+New+York,+United+States
        "api_key": serp_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    newsResults = results["local_results"]

    # Return top 3 response from list
    return newsResults[:3]
    # return results



# Trends Search
def GoogleTrendsSearch(query : str) -> list:
    """ This function will take query as an input and 
        will use serpapi to fetch query response and 
        return list of Trends
    """

    params = {
        "engine": "google_trends",
        "q": "coffee,milk,bread,pasta,steak",
        "data_type": "TIMESERIES",
        "api_key": serp_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    newsResults = results["interest_over_time"]

    # Return all responses
    return newsResults



# Finance Search
def GoogleFinanceSearch(query : str) -> list:
    """ This function will take query as an input and 
        will use serpapi to fetch query response and 
        return list of finance
    """

    params = {
        "engine": "google_finance",
        "q": query,
        "api_key": serp_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Return all responses
    return results


if __name__ == "__main__":
    # print(GoogleTextSearch('dogs')[:3])
    # print(GoogleImageSearch('dinosaurs'))
    # print(GoogleMapsSearch('fruit','delhi india'))
    # print(GoogleTrendsSearch('coffee milk bread'))
    # print(GoogleFinanceSearch('tata steel'))
    pass