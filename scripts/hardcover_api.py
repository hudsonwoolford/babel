import requests
import json
from dotenv import load_dotenv
import os

load_dotenv("api_keys.env")
URL = "https://api.hardcover.app/v1/graphql"
HEADERS = headers = {
    "Content-Type" : "application/json",
    "Authorization" : os.environ.get("HARDCOVER_AUTHORIZATION")
}
BOOK_INFO = """id
            title
            subtitle
            release_date
            description
            rating
            ratings_count
            slug
            cached_tags
            contributions {
                author {
                    name
                }
            }
            image {
                url
            }"""

def send_request(query: str) -> dict:
    """Sends a custom query to the hardcover api

    Args:
        query (str): graphql query

    Returns:
        dict: response data
    """

    return requests.post(URL, json={"query" : query}, headers=HEADERS).json()

def get_trending_ids(from_date: str, to_date: str, limit: int = 10, offset: int = 0) -> dict:
    """Gets the trending ids from hardcover

    Args:
        from_date (str): earlier date, yyyy-mm-dd
        to_date (str): later date, yyyy-mm-dd
        limit (int, optional): limit of number of books to return. Defaults to 10.
        offset (int, optional): start index. Defaults to 0.
    
    Returns:
        dict: response data
    """
    def limited_query(limit: int, offset: int) -> dict:
        query = """
        {
            books_trending (
                from: "%s"
                to: "%s"
                limit: %d
                offset: %d
            ) {
                ids
                error
            }
        }
        """ % (from_date, to_date, limit, offset)
        
        response = requests.post(URL, json={"query" : query}, headers=HEADERS)
        return response.json()

    remaining = limit

    iter = 0
    trending_ids = []
    local_limit = min(remaining, 100)
    while remaining > 0:
        print(f"Retrieving trending books {remaining} remaining")

        response = limited_query(local_limit, offset + 100 * iter) 

        #in case there is no more trending books
        try:
            data = response["data"]
        except:
            break
        
        trending_ids += list(map(str, data["books_trending"]["ids"]))

        iter += 1
        remaining -= 100
        local_limit = min(remaining, 100)
    
    return trending_ids

def get_books_by_id(ids: list) -> dict:
    """Gets book information from a list of ids

    Args:
        ids (list): book ids

    Returns:
        dict: response data
    """

    query = """
    query getBookByIdMultiple($ids: [Int!]) {
        books(where: {id: {_in: $ids}}) {
            %s
        }
    }
    """ % BOOK_INFO

    N = len(ids)
    multiples = N // 1000
    remainder = N % 1000

    # if remainder > 0:
    response = requests.post(URL, json = {"query" : query, "variables" : {"ids" : ids[:remainder]}}, headers=HEADERS)
    book_data = response.json()

    for i in range(multiples):
        print(f"{(multiples - i) * 1000} remaining" )
        local_response = requests.post(URL, json = {"query" : query, "variables" : {"ids" : ids[remainder + i * 1000:remainder + (i+1) * 1000]}}, headers=HEADERS)
        local_data = local_response.json()

        book_data["data"]["books"] += local_data["data"]["books"]


    return book_data

def get_book_by_id(id: int) -> dict:
    """Get information from a single book id

    Args:
        id (int): book id

    Returns:
        dict: response data
    """

    query = """
    query GetBook($id: Int!) {
        books(where: {id: {_eq: $id}}) {
            %s
        }
    }
    """ % BOOK_INFO

    response = requests.post(URL, json={"query" : query, "variables" : {"id" : id}}, headers=HEADERS)
    return response.json()

def format_book_data(book_data: dict) -> dict:
    """Cleans and formats the book data (raw response)

    Args:
        ids (list): book ids

    Returns:
        dict: final cleaned and formatted data
    """

    book_list = book_data["data"]["books"]

    for book in book_list:
        #clean up authors
        contributions = book["contributions"]
        book.pop("contributions")
        
        authors = [contr["author"]["name"] for contr in contributions]

        book["authors"] = authors

        #clean up tags
        cached_tags = book.get("cached_tags", {})
        book.pop("cached_tags")

        #genres
        genres = cached_tags.get("Genre", [])
        genre_counts = [g["count"] for g in genres]
        genres = [g["tag"] for g in genres]
        book["genres"] = {"names": genres, "counts": genre_counts}

        #moods
        moods = cached_tags.get("Mood",[])
        mood_counts = [m["count"] for m in moods]
        moods = [m["tag"] for m in moods]
        book["moods"] = {"names": moods, "counts": mood_counts}
    
    return book_data

def main():
    print("Retrieving ids...")
    # trending_ids = get_trending_ids("2025-01-01", "2025-04-01", limit=500, offset=0)
    with open("input/trending_ids.txt") as f:
        trending_ids = [int(l.rstrip()) for l in f]
    trending_ids = trending_ids[:30000]
    
    print("Retrieving books...")
    book_data = get_books_by_id(trending_ids)
    
    print("Formatting books...")
    book_data = format_book_data(book_data)

    id_2_index = {}
    books = book_data["data"]["books"]
    for i in range(len(books)):
        id_2_index[books[i]["id"]] = i
    
    with open("output/id_mapping.json", "w", encoding="utf-8") as f:
        json.dump(id_2_index, f, indent=1)

    with open("output/book_data.json", "w", encoding="utf-8") as f:
        json.dump(book_data, f, indent=1)

if __name__ == "__main__":
    main()

