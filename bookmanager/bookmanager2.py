from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import abort
import datetime
import os

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
        fields = ('id', 'title', 'writer', 'year')


book_schema = BookSchema()
books_schema = BookSchema(many=True)


# endpoint to create new book
@app.route("/book", methods=["POST"])
def add_book():
    title = request.json['title']
    writer = request.json['writer']
    year = request.json['year']

    print(title)
    date = datetime.datetime.now()
    if title.isspace() or not title or year>date.year:
        return "Invalid fields", 403

    all_books = Book.query.all()

    for bk in all_books:
        if bk.title == title:
            return "Book with that title already exists", 409

    new_book = Book(title, writer, year)

    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book), 201


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
    if book:
        return book_schema.jsonify(book)
    else:
        return "There is no such book",404

# endpoint to update book
@app.route("/book/<id>", methods=["PUT"])
def book_update(id):

    print(id)
    print(type(id))
    if id.isdigit():
        book = Book.query.get(id)
        if book:
            title = request.json['title']
            writer = request.json['writer']
            year = request.json['year']

            book.title = title 
            book.writer = writer
            book.year = year

            db.session.commit()
            return book_schema.jsonify(book)
        else:
            return "There is no such book",404
    else:
        books = Book.query.all()
        for b in books:
            if id == b.title:
                book = b
                if book:
                    title = request.json['title']
                    writer = request.json['writer']
                    year = request.json['year']

                    book.title = title 
                    book.writer = writer
                    book.year = year

                    db.session.commit()
                    return book_schema.jsonify(book)
                else:
                    return "There is no such book",404
            


# endpoint to delete book
@app.route("/book/<id>", methods=["DELETE"])
def book_delete(id):
    book = Book.query.get(id)
    if book:
        db.session.delete(book)
        db.session.commit()

        return book_schema.jsonify(book)
    else:
        return "There is no such book",404


if __name__ == '__main__':
    app.run(debug=True)