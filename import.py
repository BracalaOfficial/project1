import csv
import os

from sqlalchemy import create_engine, orm

engine = create_engine(os.getenv("DATABASE_URL"))
db = orm.scoped_session(orm.sessionmaker(bind=engine))

def main():
    f = open('books.csv')
    reader = csv.reader(f)

    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {'isbn': isbn, 'title': title, 'author': author, 'year': year})

        print(f"Added book {title} which is written {year}. year by {author} with ISBN: {isbn}")

    db.commit()

if __name__ == '__main__':
    main()