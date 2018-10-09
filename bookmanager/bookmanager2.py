import os

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdb2.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)
ma = Marshmallow(app)




class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable = False)
    writer = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=True)

    def __init__(self, title, writer, year):
        self.title = title
        self.writer = writer
        self.year = year
        


class BookSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('title', 'writer', 'year')


book_schema = BookSchema()
books_schema = BookSchema(many=True)


# endpoint to create new book
@app.route("/book", methods=["POST"])
def add_book():
    title = request.json['title']
    writer = request.json['writer']
    year = request.json['year']

    new_book = Book(title, writer, year)

    db.session.add(new_book)
    db.session.commit()

    return jsonify(new_book)


# endpoint to show all books
@app.route("/book", methods=["GET"])
def get_book():
    all_books = Book.query.all()
    result = books_schema.dump(all_books)
    return jsonify(result.data)


# endpoint to get book detail by id
@app.route("/book/<id>", methods=["GET"])
def book_detail(id):
    book = Book.query.get(id)
    return book_schema.jsonify(book)


# endpoint to update book
@app.route("/book/<id>", methods=["PUT"])
def book_update(id):
    book = Book.query.get(id)
    title = request.json['title']
    writer = request.json['writer']
    year = request.json['year']

    book.title = title 
    book.writer = writer
    book.year = year

    db.session.commit()
    return book_schema.jsonify(book)


# endpoint to delete book
@app.route("/book/<id>", methods=["DELETE"])
def book_delete(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()

    return book_schema.jsonify(book)


if __name__ == '__main__':
    app.run(debug=True)