import requests
import os

URL = "https://api.hardcover.app/v1/graphql"
HEADERS = headers = {
    "Content-Type" : "application/json",
    "Authorization" : os.environ.get("HARDCOVER_AUTHORIZATION")
}

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
            id
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
            }
        }
    }
    """

    response = requests.post(URL, json={"query" : query, "variables" : {"id" : id}}, headers=HEADERS)
    return response.json()
