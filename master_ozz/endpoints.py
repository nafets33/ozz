from fastapi import FastAPI, Query
from google_search_functions import (GoogleImageSearch, GoogleTextSearch, GoogleShoppingSearch, GoogleNewsSearch,
                                     GoogleMapsSearch, GoogleTrendsSearch, GoogleFinanceSearch)

app = FastAPI()


# For Google Text Search
@app.get("/google_text_search/")
async def search_text(query: str = Query(..., title="Search Query")):
    """On Frontend, call http://127.0.0.1:8000/google_text_search/?query=<your_search_query> to get list as response"""

    searchResults = GoogleTextSearch(query)
    return {"text_urls": searchResults}


# For Google Search Image 
@app.get("/google_image_search/")
async def search_images(query: str = Query(..., title="Search Query")):
    """On Frontend, call http://127.0.0.1:8000/google_image_search/?query=<your_search_query> to get image urls as response"""

    searchResults = GoogleImageSearch(query)
    return {"image_urls": searchResults}


# For Google Search Shopping 
@app.get("/google_shopping_search/")
async def search_shopping(query: str = Query(..., title="Search Query")):
    """On Frontend, call http://127.0.0.1:8000/google_shopping_search/?query=<your_search_query> to get shopping results as response"""

    searchResults = GoogleShoppingSearch(query)
    return {"shopping_results": searchResults}


# For Google Search News 
@app.get("/google_news_search/")
async def search_news(query: str = Query(..., title="Search Query")):
    """On Frontend, call http://127.0.0.1:8000/google_news_search/?query=<your_search_query> to get news results as response"""

    searchResults = GoogleNewsSearch(query)
    return {"news_results": searchResults}


# For Google Search Finance 
@app.get("/google_finance_search/")
async def search_finance(query: str = Query(..., title="Search Query")):
    """On Frontend, call http://127.0.0.1:8000/google_finance_search/?query=<your_search_query> to get results as response"""

    searchResults = GoogleFinanceSearch(query)
    return {"finance_results": searchResults}


# For Google Search Maps 
@app.get("/google_maps_search/")
async def search_maps(query: str = Query(..., title="Search Query"), location: str = Query(..., title="Location Query")):
    """On Frontend, call http://127.0.0.1:8000/google_maps_search/?query=<your_search_query>&location=<location> to get  results as response"""

    searchResults = GoogleMapsSearch(query, location)
    return {"maps_results": searchResults}


# For Google Search Trends
@app.get("/google_trends_search/")
async def search_trends(query: str = Query(..., title="Search Query")):
    """On Frontend, call http://127.0.0.1:8000/google_trends_search/?query=<your_search_query> to get results as response"""

    searchResults = GoogleTrendsSearch(query)
    return {"trends_results": searchResults}


