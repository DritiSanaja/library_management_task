INSERT INTO Author (Name) VALUES
('George Orwell'), 
('Harper Lee');

INSERT INTO Genre (Name) VALUES
('Fiction'), 
('Romance');

INSERT INTO Publisher (Name) VALUES
('Penguin Books'), 
('J.B. Lippincott & Co.');

INSERT INTO UserAccount (Name) VALUES
('Alice'), 
('Bob');

INSERT INTO Book (Title, State, AuthorID, GenreID, PublisherID) VALUES
('1984', 'Present', 1, 1, 1),
('To Kill a Mockingbird', 'Present', 2, 1, 2);

INSERT INTO BorrowTransaction (BookID, UserID, BorrowDate, ReturnDate) VALUES
(1, 1, '2025-04-01', NULL);
