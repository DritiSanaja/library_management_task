# Library Management System – Flask + PostgreSQL + Docker
Dynamic, database-driven library management system with support for book borrowing, returning, and catalog browsing. I used Flask, PostgreSQL, and containerized using Docker for setup and deployment.

# features

- view and manage a catalog of books, authors, genres, and publishers
- borrow and return books (with persistent state)
- prevents multiple users from borrowing the same book
- postgreSQL database used instead of static XML files
- fully containerized with Docker + Docker Compose

---


### steps to run with docker:
1. Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop) is installed and running.
2. Open terminal in the project folder.
3. Start the app:
```bash
docker-compose up --build
```
4. Visit in browser:
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


### Steps
1. Open cmd/terminal and clone the repository (ensure git is installed or use GutHub Desktop)
```bash
git clone https://github.com/clumsyspeedboat/library_management_task.git
```
2. "cd" into the repository
```bash
cd <path_to_your_dir>/library_management_task
```
3. Create virtual environment (ensure python is installed and added to PATH)
```bash
python -m venv env
```
4. Activate virtual environment
```bash
env\Scripts\activate # on Windows
source env/bin/activate # on Linux/Mac
```
5. Install dependencies/packages
```bash
pip install -r requirements.txt
```
5. Run Flask app
```bash
python app.py
```
6. Navigate to localhost (port will be displayed in terminal)
```bash
http://localhost:5000 # Most probably
```
