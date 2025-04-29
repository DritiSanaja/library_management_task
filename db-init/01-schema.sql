-- Author Table
CREATE TABLE Author (
    AuthorID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

-- Genre Table
CREATE TABLE Genre (
    GenreID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

-- Publisher Table
CREATE TABLE Publisher (
    PublisherID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

-- User Table
CREATE TABLE UserAccount (
    UserID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

-- Book Table
CREATE TABLE Book (
    BookID SERIAL PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    State VARCHAR(50),
    AuthorID INT NOT NULL,
    GenreID INT NOT NULL,
    PublisherID INT NOT NULL,
    FOREIGN KEY (AuthorID) REFERENCES Author(AuthorID),
    FOREIGN KEY (GenreID) REFERENCES Genre(GenreID),
    FOREIGN KEY (PublisherID) REFERENCES Publisher(PublisherID)
);

-- BorrowTransaction Table
CREATE TABLE BorrowTransaction (
    TransactionID SERIAL PRIMARY KEY,
    BookID INT NOT NULL,
    UserID INT NOT NULL,
    BorrowDate DATE NOT NULL,
    ReturnDate DATE,
    FOREIGN KEY (BookID) REFERENCES Book(BookID),
    FOREIGN KEY (UserID) REFERENCES UserAccount(UserID)
);
