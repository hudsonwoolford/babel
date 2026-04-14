import requests
import json
import pandas as pd

def get_books(url_end="", **kwargs):
    url = "https://www.googleapis.com/books/v1/volumes" + url_end
    # print(url)

    try:
        response = requests.get(url, params=kwargs)

        if response.status_code == 200:
            book = response.json()
            return book
        else:
            print("Error: ", response.status_code)
            return None
        
    except requests.exceptions.RequestException as e:
        print("Error:", e)

# with open("output/google_books.json", mode="w") as f:
#     # response = get_books(printType="books", langRestrict="en", key="**SECRET**")
#     response = get_books(q="isbn:1594634025",key="**SECRET**", printType="books", langRestrict="en")
#     json.dump(response, f, indent=1)

with open("input/BestsellingISBNs.txt") as f:
    locators = f.readlines()
    
with open("output/google_books.json", mode="w") as f:
    f.write("")

with open("output/google_books.json", mode="a") as f:
    total_response = {}
    id_counter=-1
    for i in range(450):
        response={}
        try:
            print("Getting book:", locators[i])
            response = get_books(q=f"isbn:{locators[i]}", printType="books", langRestrict="en", key="**SECRET**")
            if response["totalItems"] == 1:
                response = get_books(url_end=f"/{response["items"][0]["id"]}", key="**SECRET**")
            else:
                continue
            id_counter+=1
        except Exception as e:
            print("Invalid ISBN:", locators[i])
            print(e)
            
        total_response[str(id_counter)] = response
        
    json.dump(total_response, f, indent=1)
        




# df = pd.read_csv("input/BestsellerBooks.csv", encoding="utf-8")

# with open("output/BestsellingISBNs.txt", mode="w", encoding="utf-8") as f:
#     f.write('\n'.join([str(isbn) for isbn in df.primary_isbn10 if str(isbn) != "nan"]))
