from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import configparser
import requests
import logging
from flask_cors import CORS
from neo4j import GraphDatabase
import os
db_host = os.getenv("DB_HOST", "localhost")
db_pass = os.getenv("DB_PASSWORD", "password")


app = Flask(__name__, static_url_path='/static', static_folder='static')
# database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{db_pass}@db:5432/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)

CORS(app)

# database models

class Author(db.Model):
    __tablename__ = 'author'
    AuthorID = db.Column('authorid', db.Integer, primary_key=True)
    Name = db.Column('name', db.String(255), nullable=False)

class Genre(db.Model):
    __tablename__ = 'genre'
    GenreID = db.Column('genreid', db.Integer, primary_key=True)
    Name = db.Column('name', db.String(255), nullable=False)

class Publisher(db.Model):
    __tablename__ = 'publisher'
    PublisherID = db.Column('publisherid', db.Integer, primary_key=True)
    Name = db.Column('name', db.String(255), nullable=False)

class Book(db.Model):
    __tablename__ = 'book'
    BookID = db.Column('bookid', db.Integer, primary_key=True)
    Title = db.Column('title', db.String(255), nullable=False)
    State = db.Column('state', db.String(50))
    AuthorID = db.Column('authorid', db.Integer, db.ForeignKey('author.authorid'), nullable=False)
    GenreID = db.Column('genreid', db.Integer, db.ForeignKey('genre.genreid'), nullable=False)
    PublisherID = db.Column('publisherid', db.Integer, db.ForeignKey('publisher.publisherid'), nullable=False)

class UserAccount(db.Model):
    __tablename__ = 'useraccount'
    UserID = db.Column('userid', db.Integer, primary_key=True)
    Name = db.Column('name', db.String(255), nullable=False)

class BorrowTransaction(db.Model):
    __tablename__ = 'borrowtransaction'
    TransactionID = db.Column('transactionid', db.Integer, primary_key=True)
    BookID = db.Column('bookid', db.Integer, db.ForeignKey('book.bookid'), nullable=False)
    UserID = db.Column('userid', db.Integer, db.ForeignKey('useraccount.userid'), nullable=False)
    BorrowDate = db.Column('borrowdate', db.Date, nullable=False)
    ReturnDate = db.Column('returndate', db.Date)

#connect to neo4j
neo4j_driver = GraphDatabase.driver(
    "bolt://neo4j:7687", 
    auth=("neo4j", "password")
)

# Configure logging to DEBUG level for detailed logs
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Load the configuration from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the API key and URL from the configuration
try:
    GEMINI_API_KEY = config.get('API', 'GEMINI_API_KEY')
    GEMINI_API_URL = config.get('API', 'GEMINI_API_URL')
    logging.info("Gemini API configuration loaded successfully.")
except Exception as e:
    logging.error("Error reading config.ini: %s", e)
    GEMINI_API_KEY = None
    GEMINI_API_URL = None

# Route to serve the home page
@app.route('/')
def home():
    return render_template('index.html')

#testing route
@app.route('/api/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([{'id': a.AuthorID, 'name': a.Name} for a in authors])


# Route to serve viewer.html
@app.route('/viewer.html')
def viewer():
    return render_template('viewer.html')

# too see who borrowed the book
def get_latest_borrower_name(book_id):
    tx = BorrowTransaction.query.filter_by(BookID=book_id).order_by(BorrowTransaction.BorrowDate.desc()).first()
    if tx and tx.UserID:
        user = UserAccount.query.get(tx.UserID)
        return user.Name if user else 'Unknown'
    return ''

#find the book last trasnaciton and show in ui
def get_latest_borrow_date(book_id):
    tx = BorrowTransaction.query.filter_by(BookID=book_id).order_by(BorrowTransaction.BorrowDate.desc()).first()
    return tx.BorrowDate.strftime('%Y-%m-%d') if tx and tx.BorrowDate else ''

#display the return date
def get_latest_return_date(book_id):
    tx = BorrowTransaction.query.filter_by(BookID=book_id).order_by(BorrowTransaction.BorrowDate.desc()).first()
    return tx.ReturnDate.strftime('%Y-%m-%d') if tx and tx.ReturnDate else ''


@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([
        {
            'id': book.BookID,
            'title': book.Title,
            'state': book.State,
            'author': Author.query.get(book.AuthorID).Name if book.AuthorID else 'Unknown',
            'genre': Genre.query.get(book.GenreID).Name if book.GenreID else 'Unknown',
            'publisher': Publisher.query.get(book.PublisherID).Name if book.PublisherID else 'Unknown',
            'borrower': get_latest_borrower_name(book.BookID),
            'borrowDate': get_latest_borrow_date(book.BookID),
            'returnDate': get_latest_return_date(book.BookID)
        }
        for book in books
    ])


# API route to fetch description from Gemini API
@app.route('/api/description', methods=['GET'])
def get_description():
    entity_name = request.args.get('name')
    logging.debug(f"Received request for entity name: {entity_name}")  # Changed to DEBUG

    if not entity_name:
        logging.warning("Missing entity name in request.")
        return jsonify({'error': 'Missing entity name'}), 400

    if not GEMINI_API_URL or not GEMINI_API_KEY:
        logging.error("Gemini API configuration missing.")
        return jsonify({'error': 'Server configuration error'}), 500

    # Prepare the JSON payload with explicit instructions
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Provide a detailed description of '{entity_name}'"
                            "If it is a book include information about the setting, characters, themes, key concepts, and its influence. "
                            "Do not include any concluding remarks or questions."
                            "Do not mention any Note at the end about not including concluding remarks or questions."
                        )
                    }
                ]
            }
        ]
    }

    # Construct the API URL with the API key as a query parameter
    api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    # Log the API URL and payload for debugging
    logging.debug(f"API URL: {api_url_with_key}")
    logging.debug(f"Payload: {payload}")

    try:
        # Make the POST request to the Gemini API
        response = requests.post(
            api_url_with_key,  # Include the API key in the URL
            headers=headers,
            json=payload,
            timeout=10  # seconds
        )
        logging.debug(f"Gemini API response status: {response.status_code}")  # Changed to DEBUG

        if response.status_code != 200:
            logging.error(f"Failed to fetch description from Gemini API. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            return jsonify({
                'error': 'Failed to fetch description from Gemini API',
                'status_code': response.status_code,
                'response': response.text
            }), 500

        response_data = response.json()
        # Extract the description from the response
        description = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No description available.')
        logging.debug(f"Fetched description: {description}")  # Changed to DEBUG

        return jsonify({'description': description})

    except requests.exceptions.RequestException as e:
        logging.error(f"Exception during Gemini API request: {e}")
        return jsonify({'error': 'Failed to connect to Gemini API', 'message': str(e)}), 500
    except ValueError as e:
        logging.error(f"JSON decoding failed: {e}")
        return jsonify({'error': 'Invalid JSON response from Gemini API', 'message': str(e)}), 500
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500

@app.route('/api/graph/books', methods=['GET'])
def get_books_graph():
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (b:Book)-[:WRITTEN_BY]->(a:Author),
                  (b)-[:BELONGS_TO]->(g:Genre),
                  (b)-[:PUBLISHED_BY]->(p:Publisher)
            RETURN b.BookID as id, b.Title as title, a.Name as author, g.Name as genre, p.Name as publisher
        """)
        books = [record.data() for record in result]
    return jsonify(books)


@app.route('/api/book/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    data = request.get_json()
    borrower_name = data.get('borrowerName')
    borrow_date = data.get('borrowDate')

    # Fetch the book from the database
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'message': 'Book not found'}), 404

    # Check if the book is already borrowed
    if book.State == 'Borrowed':
        return jsonify({'success': False, 'message': 'Book already borrowed'}), 400

    # Update the book state to "Borrowed"
    book.State = 'Borrowed'

    # Create a new borrow transaction
    transaction = BorrowTransaction(
        BookID=book_id,
        UserID=1,  
        BorrowDate=borrow_date
    )

    try:
        # Add the transaction to the session
        db.session.add(transaction)
        
        # Commit the transaction and update the book state
        db.session.commit()

        # Return a success response
        return jsonify({'success': True, 'message': 'Book borrowed successfully'})
    
    except Exception as e:
        # Rollback the session if there is an error
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500




@app.route('/api/return/<int:book_id>', methods=['POST'])
def return_book(book_id):
    data = request.get_json()  # This is where you're expecting the JSON body
    return_date = data.get('returnDate')

    # Debugging: Print the data to see if it's correctly received
    print(f"Received return request for Book ID {book_id} with returnDate: {return_date}")

    # Fetch the book and check its status
    book = Book.query.get(book_id)
    if not book or book.State != 'Borrowed':
        return jsonify({'success': False, 'message': 'Book is not borrowed'}), 400

    book.State = 'Present'
    db.session.commit()

    transaction = BorrowTransaction.query.filter_by(BookID=book_id).order_by(BorrowTransaction.BorrowDate.desc()).first()
    if transaction:
        transaction.ReturnDate = return_date
        db.session.commit()

    return jsonify({'success': True, 'message': 'Book returned successfully'})



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")