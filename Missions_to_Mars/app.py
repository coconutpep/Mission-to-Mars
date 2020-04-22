from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# Or set inline
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

@app.route("/")
def index():
    dictionary = mongo.db.data.find_one()
    return render_template("index.html", dictionary=dictionary)


@app.route("/scrape")
def scraper():
    dictionary = mongo.db.data
    dictionary_data = scrape_mars.scrape()
    dictionary.update({}, dictionary_data, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)