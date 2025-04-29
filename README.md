# Library Management System – Flask + PostgreSQL + Neo4j + Docker

A dynamic, database-driven library management system built with **Flask**, backed by a **PostgreSQL** relational database and now extended to **Neo4j** for advanced graph-based data querying. Fully containerized using Docker for easy setup and deployment.

---

## Features

- View and manage a catalog of books, authors, genres, and publishers
- Borrow and return books with persistent state tracking
- Prevents multiple users from borrowing the same book concurrently
- Uses PostgreSQL (instead of static XML files)
- Migrates relational data to Neo4j for graph queries
- Fully containerized with Docker + Docker Compose

---

## Running with Docker

1. Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop) is installed and running.
2. Open terminal in the project folder.
3. Start the application:
   ```bash
   docker-compose up --build
   ```
4. Visit the app in your browser:
   ```
   http://localhost:5000
   ```
5. To stop the app:
   ```bash
   docker-compose down
   ```
6. To reset the database:
   ```bash
   docker-compose down -v
   ```

---

## Manual Setup (Without Docker)

1. Clone the repository:
   ```bash
   git clone https://github.com/clumsyspeedboat/library_management_task.git
   ```
2. Navigate into the project directory:
   ```bash
   cd library_management_task
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv env
   env\Scripts\activate      # Windows
   source env/bin/activate   # Linux/Mac
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the Flask app:
   ```bash
   python app.py
   ```
6. Open your browser:
   ```
   http://localhost:5000
   ```

---

## Data Migration to Neo4j

To migrate data from PostgreSQL to Neo4j:

1. Ensure PostgreSQL and Neo4j are both running.
2. Run the migration script:
   ```bash
   python Migrate.py
   ```
3. This will:
   - Create nodes: `Author`, `Book`, `Genre`, `Publisher`, `User`
   - Create relationships:
     - `(:Book)-[:WRITTEN_BY]->(:Author)`
     - `(:Book)-[:BELONGS_TO]->(:Genre)`
     - `(:Book)-[:PUBLISHED_BY]->(:Publisher)`
     - `(:User)-[:BORROWED {BorrowDate, ReturnDate}]->(:Book)`

⚠️ If `ReturnDate` is null, it will be excluded from the relationship to avoid errors.

---

## Sample Neo4j Queries

```cypher
// Find all books by a specific author
MATCH (a:Author {Name: "George Orwell"})<-[:WRITTEN_BY]-(b:Book)
RETURN b.Title;

// List users who borrowed a particular book
MATCH (b:Book {Title: "1984"})<-[:BORROWED]-(u:User)
RETURN u.Name, b.Title;
```

---

## Project Structure

```
library_management_task/
│
├── app.py               # Flask application entry point
├── Migrate.py           # Script to migrate relational data to Neo4j
├── models.py            # SQLAlchemy models
├── templates/           # HTML templates
├── static/              # CSS/JS assets
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker orchestration
└── README.md
```

---

## 📄 License

[MIT](LICENSE)
