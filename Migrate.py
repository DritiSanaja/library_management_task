from app import app, db, Author, Book, Genre, Publisher, UserAccount, BorrowTransaction
from neo4j import GraphDatabase
import time
import psycopg2
import os

for i in range(10):
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="library",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "password")
        )
        conn.close()
        break
    except psycopg2.OperationalError:
        print("Database not ready yet, retrying in 3 seconds...")
        time.sleep(3)
else:
    raise Exception("Database connection failed after retries")

neo4j_driver = GraphDatabase.driver(
    "bolt://neo4j:7687",
    auth=("neo4j", "password")
)

def migrate_data():
    with neo4j_driver.session() as session:
        # Authors
        for author in Author.query.all():
            session.run("MERGE (a:Author {AuthorID: $id, Name: $name})",
                        id=author.AuthorID, name=author.Name)

        # Genres
        for genre in Genre.query.all():
            session.run("MERGE (g:Genre {GenreID: $id, Name: $name})",
                        id=genre.GenreID, name=genre.Name)

        # Publishers
        for publisher in Publisher.query.all():
            session.run("MERGE (p:Publisher {PublisherID: $id, Name: $name})",
                        id=publisher.PublisherID, name=publisher.Name)

        # Users
        for user in UserAccount.query.all():
            session.run("MERGE (u:User {UserID: $id, Name: $name})",
                        id=user.UserID, name=user.Name)

        # Books + Relationships
        for book in Book.query.all():
            session.run("""
                MERGE (b:Book {BookID: $id, Title: $title, State: $state})
                WITH b
                MATCH (a:Author {AuthorID: $author_id})
                MERGE (b)-[:WRITTEN_BY]->(a)
                WITH b
                MATCH (g:Genre {GenreID: $genre_id})
                MERGE (b)-[:BELONGS_TO]->(g)
                WITH b
                MATCH (p:Publisher {PublisherID: $publisher_id})
                MERGE (b)-[:PUBLISHED_BY]->(p)
            """, id=book.BookID, title=book.Title, state=book.State,
                 author_id=book.AuthorID, genre_id=book.GenreID, publisher_id=book.PublisherID)

        # Borrow Transactions
        for tx in BorrowTransaction.query.all():
            session.run("""
                MATCH (u:User {UserID: $user_id})
                MATCH (b:Book {BookID: $book_id})
                MERGE (u)-[r:BORROWED {
                    BorrowDate: $borrow_date
                }]->(b)
                SET r.ReturnDate = $return_date
            """,
            user_id=tx.UserID,
            book_id=tx.BookID,
            borrow_date=str(tx.BorrowDate),
            return_date=str(tx.ReturnDate) if tx.ReturnDate else None)

if __name__ == '__main__':
    with app.app_context():
        migrate_data()
        print("Migration completed.")
