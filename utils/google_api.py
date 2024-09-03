from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = 'AIzaSyBf719x1yQKQKmy1v0yuFOsXWWpG2vPf7c'
CSE_ID = '3707af7df34764449'


def search_google(query):
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        res = service.cse().list(q=query, cx=CSE_ID, num=5).execute()

        if 'items' in res:
            results = []
            for item in res['items']:
                results.append({
                    'title': item['title'],
                    'snippet': item['snippet'],
                    'link': item['link']
                })
            return format_search_results(results)
        else:
            return "No results found."
    except HttpError as e:
        return f"An error occurred: {e}"


def format_search_results(results):
    formatted = "Here are the top search results:\n\n"
    for i, result in enumerate(results, 1):
        formatted += f"{i}. {result['title']}\n"
        formatted += f"   {result['snippet']}\n"
        formatted += f"   Link: {result['link']}\n\n"
    return formatted