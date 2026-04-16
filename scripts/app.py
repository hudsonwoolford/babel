import json
import numpy as np
import vector_utils
import random
from recommender import LinUCB, Rocchio
from flask import Flask, render_template, session, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "bindr-session"

BOOKS = None
ID_2_INDEX = None
VECTORS = None
RECOMMEND = None
SESSION_LENGTH = 20

def init_session():
    global BOOKS, ID_2_INDEX, VECTORS, RECOMMEND

    with open("output/book_data.json") as f:
        BOOKS = json.load(f)["data"]["books"]

    with open("output/id_mapping.json") as f:
        ID_2_INDEX = json.load(f)
        ID_2_INDEX = {int(key):value for key, value in ID_2_INDEX.items()}
    
    VECTORS = np.load("output/book_vectors.npy")
    
    # RECOMMEND = LinUCB(VECTORS, ID_2_INDEX, alpha=0)
    RECOMMEND = LinUCB(VECTORS)

@app.route('/logout')
def logout():
    session.clear()
    return "Logged out and session cleared!"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/library")
def library():
    fav_ids = session.get("fav_ids", [])
    favorites = [BOOKS[ID_2_INDEX[book_id]] for book_id in fav_ids]

    recommended = random.sample(range(len(VECTORS)), 10)
    recommended = [BOOKS[ind] for ind in recommended]
    return render_template("library.html", favorites=favorites, recommended=recommended)

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/match")
def match():
    session["session_ids"] = []


    # if len(seen_ids) < 5:
    #     index = random.choice(range(min(len(VECTORS), 150)))
    # else:
    


    return redirect(url_for("swipe_session"))

@app.route("/match/session")
def swipe_session():
    session_ids = session.get("session_ids", [])
    seen_ids = session.get("seen_ids", [])
    seen_indices = [ID_2_INDEX[b_id] for b_id in seen_ids]
    index = RECOMMEND.recommend(seen_indices)
    return render_template("match.html",
                        book=BOOKS[index],
                        n_swipes=len(session_ids),
                        max_swipes=SESSION_LENGTH)




@app.route("/summary")
def summary():
    liked_ids = session.get("liked_ids", [])
    liked_books = [BOOKS[ID_2_INDEX[book_id]] for book_id in liked_ids]
    
    fav_ids = session.get("fav_ids", [])
    # fav_books = [BOOKS[ID_2_INDEX[book_id]] for book_id in fav_ids]

    rec_books = random.sample(range(len(VECTORS)), 10)
    rec_books = [BOOKS[ind] for ind in rec_books]

    return render_template('summary.html', liked_books=liked_books, rec_books=rec_books, fav_ids=fav_ids)

@app.route("/favorite", methods=["POST"])
def favorite():
    book_id = int(request.form.get("book_id", -1))
    endpoint = request.form.get("endpoint", 'summary')

    fav_ids = session.get("fav_ids", [])
    if book_id in set(fav_ids):
        fav_ids.remove(book_id)
    else:
        fav_ids.append(book_id)

    session["fav_ids"] = fav_ids

    return redirect(url_for(endpoint))

@app.route("/swipe", methods=["POST"])
def swipe():
    book_id = int(request.form.get("book_id", -1))

    seen_ids = session.get("seen_ids", [])
    seen_ids.append(book_id)
    session["seen_ids"] = seen_ids
    session_ids = session.get("session_ids", [])
    session_ids.append(book_id)
    session["session_ids"] = session_ids


    direction = request.form.get("direction")
    if direction == "right":
        liked_ids = session.get("liked_ids", [])
        liked_ids.append(book_id)
        session["liked_ids"] = liked_ids

        RECOMMEND.update(ID_2_INDEX[book_id], True)
    elif direction == "left":
        RECOMMEND.update(ID_2_INDEX[book_id], False)
    
    if len(session_ids) < SESSION_LENGTH:
        return redirect(url_for("swipe_session"))
    else:
        return redirect(url_for('summary'))

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
