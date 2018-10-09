import os

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect

from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdb.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Book(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    #writer = db.Column(db.String(50), nullable=False)
    #id = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return "<Title: {}>".format(self.title)

@app.route("/", methods=["GET"])
def home(): 
    books = Book.query.all()
    for b in books:
        if b.title == "" or b.title.isspace():
            db.session.delete(b)
            db.session.commit()
    return render_template("home.html", books=books)

@app.route("/resource/book", methods=["GET"])
def getBook(): 
        #books = Book.query.get(request.form.get("title"))
        #book = Book(title=request.form.get("title"))
    ttl = request.args.get('title')
    books = Book.query.filter_by(title=ttl).all()
    return render_template("home.html", books=books)

@app.route("/resource/book/<title>", methods=["GET"])
def BookDetails(title): 
    books = Book.query.get(title)
    return render_template("book.html", book = books)

@app.route("/resource/book/<title>", methods=["POST"])
def UpdateBook(title):
    if request.form:
        book = Book.query.get(title)
        method = request.form.get("_method")
        print(method)
        if method == 'UPDATE':
            print("update")
            newtitle = request.form.get("newtitle")
            oldtitle = request.form.get("oldtitle")
            book.title = newtitle
            db.session.commit()
            return render_template("book.html", book = book)
        if method == "DELETE":
            print("delete")
            db.session.delete(book)
            db.session.commit()
            return redirect("/")

    return render_template("book.html", book = book)


@app.route("/resource/book", methods=["POST"])
def newBook():
    if request.form:
        if request.form.get("title") == "" or request.form.get("title").isspace():
            return render_template("home.html", books=Book.query.all())

        bs = Book.query.all()
        for b in bs:
            if b.title == request.form.get("title"):
                return render_template("home.html", books=bs)
        book = Book(title=request.form.get("title"))
        db.session.add(book)
        db.session.commit()
        books = Book.query.all()
    return render_template("home.html", books=books)

if __name__ == "__main__":
    app.run(debug=True)