import json
import numpy as np
import vector_utils
import random
from recommender import LinUCB, Rocchio
from searcher import Levenshtein
from flask import Flask, render_template, session, request, redirect, url_for, jsonify, flash, get_flashed_messages

app = Flask(__name__)
app.secret_key = "bindr-session"

BOOKS = None
ID_2_INDEX = None
VECTORS = None
RECOMMEND = None
SEARCH = None
SESSION_LENGTH = 20

def init_session():
    global BOOKS, ID_2_INDEX, VECTORS, RECOMMEND, SEARCH

    with open("output/book_data.json") as f:
        BOOKS = json.load(f)["data"]["books"][:50000]

    with open("output/id_mapping.json") as f:
        ID_2_INDEX = json.load(f)
        ID_2_INDEX = {int(key):value for key, value in ID_2_INDEX.items()}
    
    VECTORS = np.load("output/desc_vectors.npy")[:50000]
    
    # RECOMMEND = LinUCB(VECTORS, ID_2_INDEX, alpha=0)
    RECOMMEND = LinUCB(VECTORS)
    SEARCH = Levenshtein([book["title"] for book in BOOKS])


@app.route('/clear', methods=['POST'])
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")


#region Library

@app.route("/library")
def library():
    fav_ids = session.get("fav_ids", [])
    favorites = [BOOKS[ID_2_INDEX[book_id]] for book_id in fav_ids]

    recommended = random.sample(range(len(VECTORS)), 10)
    recommended = [BOOKS[ind] for ind in recommended]
    return render_template("library.html", favorites=favorites, recommended=recommended)

@app.route("/library/search", methods=["GET","POST"])
def search():
    top_books = None
    if request.method == "POST":
        query = request.form.get("search_box").strip()

        if not query:
            flash("Please enter a query", "error")
        elif len(query) > 100:
            flash("Please enter a query less than 100 characters", "error")
        else:
            top_n = SEARCH.search(query)
            top_books = [BOOKS[i] for i in top_n]


    
    fav_ids = session.get("fav_ids", [])
    return render_template("search.html", top_books=top_books, fav_ids=fav_ids)

#endregion

#region Swiping / Matching
@app.route("/match")
def match():
    session["session_ids"] = []
    session["liked_ids"] = []
    session["queued_ids"] = []

    return redirect(url_for("swipe_session"))

@app.route("/match/session")
def swipe_session():
    seen_ids = session.get("seen_ids", [])
    session_ids = session.get("session_ids", [])
    seen_indices = [ID_2_INDEX[b_id] for b_id in seen_ids]
    fav_ids = session.get("fav_ids", [])

    global RECOMMEND
    RECOMMEND = LinUCB(VECTORS)
    RECOMMEND.mass_update([ID_2_INDEX[b_id] for b_id in fav_ids])

    init_books = []
    for _ in range(3):
        init_books.append(RECOMMEND.recommend(seen_indices + init_books))

    session["queued_ids"] = [BOOKS[i]["id"] for i in init_books]
    book_queue = [BOOKS[i] for i in init_books]

    return render_template("match.html",
                        book_queue=book_queue,
                        counter=len(session_ids)+1,
                        max_swipes=SESSION_LENGTH)

@app.route("/swipe", methods=["POST"])
def swipe():
    book_id = int(request.form.get("book_id", -1))
    session_ids = add_item_session("session_ids", book_id)
    seen_ids = add_item_session("seen_ids", book_id)
    queued_ids = session.get("queued_ids", [])

    liked = request.form.get("direction") == "right"
    RECOMMEND.update(ID_2_INDEX[book_id], liked)
    if liked:
        add_item_session("liked_ids", book_id)

    counter = len(session_ids)
    if counter >= SESSION_LENGTH:
        return jsonify({"done": True, "redirect":url_for("summary")})
    
    seen_indices = [ID_2_INDEX[b_id] for b_id in seen_ids]
    queued_indices = [ID_2_INDEX[b_id] for b_id in queued_ids]

    index = RECOMMEND.recommend(seen_indices + queued_indices)
    add_item_session("queued_ids", BOOKS[index]["id"])

    return jsonify({"done": False, "book": BOOKS[index], "counter": counter+1})

@app.route("/summary")
def summary():
    liked_ids = session.get("liked_ids", [])
    print(liked_ids)
    liked_books = [BOOKS[ID_2_INDEX[book_id]] for book_id in liked_ids]

    unique_genres = set()
    for book in liked_books:
        top_genres = book["genres"]["names"][:3]
        for genre in top_genres:
            unique_genres.add(genre)
    n_genres = len(unique_genres)
    
    fav_ids = session.get("fav_ids", [])
    # fav_books = [BOOKS[ID_2_INDEX[book_id]] for book_id in fav_ids]

    rec_books = random.sample(range(len(VECTORS)), 10)
    rec_books = [BOOKS[ind] for ind in rec_books]

    return render_template('summary.html', 
                           liked_books=liked_books, 
                           rec_books=rec_books, 
                           fav_ids=fav_ids,
                           n_genres=n_genres)
    
#endregion

def add_item_session(list_name: str, item):
    list_obj = session.get(list_name, [])
    list_obj.append(item)
    session[list_name] = list_obj
    return list_obj

@app.route("/favorite", methods=["POST"])
def favorite():
    book_id = int(request.form.get("book_id", -1))

    fav_ids = session.get("fav_ids", [])
    seen_ids = session.get("seen_ids", [])
    if book_id in set(fav_ids):
        fav_ids.remove(book_id)
    else:
        fav_ids.append(book_id)
        if book_id not in set(seen_ids):
            seen_ids.append(book_id)

    session["fav_ids"] = fav_ids
    session["seen_ids"] = seen_ids

    return '', 204


@app.route("/book-info/<id>")
def book_info(id):
    book_id = int(id)

    return render_template("book-info.html", book=BOOKS[ID_2_INDEX[book_id]])

@app.template_filter('stars')
def stars(rating, max=5):
    rating = round(float(rating), 1)
    filled = round(rating)
    return f"{rating} {'★' * filled}{'☆' * (max - filled)}"

if __name__ == "__main__":
    init_session()
    app.run(debug=True)
    session.clear()
