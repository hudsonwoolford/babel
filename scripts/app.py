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

def init_session():
    global BOOKS, ID_2_INDEX, VECTORS, RECOMMEND

    with open("output/book_data.json") as f:
        BOOKS = json.load(f)["data"]["books"]

    with open("output/id_mapping.json") as f:
        ID_2_INDEX = json.load(f)
        ID_2_INDEX = {int(key):value for key, value in ID_2_INDEX.items()}
    
    VECTORS = np.load("output/book_vectors.npy")
    
    # RECOMMEND = LinUCB(VECTORS, ID_2_INDEX, alpha=0)
    RECOMMEND = Rocchio(VECTORS)

@app.route('/logout')
def logout():
    session.clear()
    return "Logged out and session cleared!"

@app.route("/")
def index():
    
    seen_ids = session.get("seen_ids", [])

    if len(seen_ids) < 5:
        index = random.choice(range(min(len(VECTORS), 150)))
    else:
        seen_indices = [ID_2_INDEX[b_id] for b_id in seen_ids]
        index = RECOMMEND.recommend(seen_indices)

    return render_template("index.html",
                           book=BOOKS[index])


@app.route("/swipe", methods=["POST"])
def swipe():
    book_id = int(request.form.get("book_id", -1))
    seen_ids = session.get("seen_ids", [])
    seen_ids.append(book_id)
    session["seen_ids"] = seen_ids

    direction = request.form.get("direction")
    if direction == "right":
        RECOMMEND.update(ID_2_INDEX[book_id], True)
    elif direction == "left":
        RECOMMEND.update(ID_2_INDEX[book_id], False)
    

    return redirect(url_for("index"))


@app.template_filter('stars')
def stars(rating, max=5):
    rating = round(float(rating), 1)
    filled = round(rating)
    return f"{rating} {'★' * filled}{'☆' * (max - filled)}"

if __name__ == "__main__":
    init_session()
    app.run(debug=True)
    session.clear()
