from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import abort
from sqlalchemy.orm import *
import datetime
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdb2.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)
ma = Marshmallow(app)




class Book(db.Model):
    __tablename__='books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable = False)
    year = db.Column(db.Integer, nullable=True)
    writer_id = db.Column(db.Integer, db.ForeignKey('writers.id'))

    def __init__(self, title, writer_id, year):
        self.title = title
        self.writer_id = writer_id
        self.year = year

class Writer(db.Model):
    __tablename__='writers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable = False)
    birth_year = db.Column(db.Integer, nullable=True)
    books = db.relationship('Book', backref='writer')

    def __init__(self, name, birth_year):
        self.name = name
        self.birth_year = birth_year

        


class BookSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'title', 'writer_id', 'year')

class WriterSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'birth_year')


book_schema = BookSchema()
books_schema = BookSchema(many=True)
writer_schema = WriterSchema()
writers_schema = WriterSchema(many=True)


# endpoint to create new book
@app.route("/book", methods=["POST"])
def add_book():
    title = request.json['title']
    writer_id = request.json['writer_id']
    year = request.json['year']

    print(title)
    date = datetime.datetime.now()
    if title.isspace() or not title or year>date.year:
        return "Invalid fields", 403

    all_books = Book.query.all()

    for bk in all_books:
        if bk.title == title:
            return "Book with that title already exists", 409

    writer = Writer.query.get(writer_id)
    if not writer:
        return "There is no writer with that id",404

    new_book = Book(title, writer_id, year)

    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book), 201

@app.route("/writer", methods=["POST"])
def add_writer():

    name = request.json['name']
    birth_year = request.json['birth_year']

    date = datetime.datetime.now()
    if name.isspace() or not name or birth_year>date.year-14:
        return "Invalid fields", 403

    all_writers = Writer.query.all()

    for wr in all_writers:
        if wr.name == name:
            return "Writer with that name already exists", 409

    new_writer = Writer(name, birth_year)

    db.session.add(new_writer)
    db.session.commit()

    return writer_schema.jsonify(new_writer), 201


# endpoint to show all books
@app.route("/book", methods=["GET"])
def get_book():
    all_books = Book.query.all()
    result = books_schema.dump(all_books)
    return jsonify(result.data)

@app.route("/writer", methods=["GET"])
def get_writer():
    all_writers = Writer.query.all()
    result = writers_schema.dump(all_writers)
    return jsonify(result.data)


# endpoint to get book detail by id
@app.route("/book/<id>", methods=["GET"])
def book_detail(id):



    if id.isdigit():
        book = Book.query.get(id)
        if book:
            return book_schema.jsonify(book)
        else:
            return "There is no such book",404
    else:
        books_res = []
        books = Book.query.all()
        for b in books:
            if id.lower() in b.title.lower():
                books_res.append(b)
        if books_res:
            return books_schema.jsonify(books_res)
        else:
            return "There is no such book",404
            

@app.route("/writer/<id>", methods=["GET"])
def writer_detail(id):
    writer = Writer.query.get(id)
    if writer:
        return writer_schema.jsonify(writer)
    else:
        return "There is no such writer",404

# endpoint to update book
@app.route("/book/<id>", methods=["PUT"])
def book_update(id):
    if id.isdigit():
        book = Book.query.get(id)
    else:
        books = Book.query.all()
        for b in books:
            if id == b.title:
                book = b

    if book:
        title = request.json['title']
        writer_id = request.json['writer_id']
        year = request.json['year']
        book.title = title 
        book.writer_id = writer_id
        book.year = year

        db.session.commit()
        return book_schema.jsonify(book)
    else:
        return "There is no such book",404


@app.route("/writer/<id>", methods=["PUT"])
def writer_update(id):
    if id.isdigit():
        writer = Writer.query.get(id)
    else:
        writers = Writer.query.all()
        for w in writers:
            if id == w.name:
                writer = w

    if writer:

        name = request.json['name']
        birth_year = request.json['birth_year']

        writer.name = name
        writer.birth_year = birth_year

        db.session.commit()
        return writer_schema.jsonify(writer)
    else:
        return "There is no such writer",404
            


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

@app.route("/writer/<id>", methods=["DELETE"])
def writer_delete(id):
    writer = Writer.query.get(id)
    if writer:
        db.session.delete(writer)
        db.session.commit()

        return writer_schema.jsonify(writer)
    else:
        return "There is no such writer",404

@app.route("/book/writer/<id>", methods=["GET"])
def get_books_writer(id):
    writer = Writer.query.get(id)
    if writer:
        books = writer.books
        return books_schema.jsonify(books)
    else:
        return "There is no such writer", 404

@app.route("/writer/book/<id>", methods=["GET"])
def get_writer_book(id):
    book = Book.query.get(id)
    if book:
        writer = book.writer
        return writer_schema.jsonify(writer)
    else:
        return "There is no such book", 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')