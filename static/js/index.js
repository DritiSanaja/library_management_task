window.onload = function () {
    fetch('/api/books')
        .then(res => res.json())
        .then(books => {
            const bookTable = document.getElementById('book-table');
            const borrowBookSelect = document.getElementById('borrowBookId');
            const returnBookSelect = document.getElementById('returnBookId');

            borrowBookSelect.innerHTML = '<option value="">Select a Book</option>';
            returnBookSelect.innerHTML = '<option value="">Select a Book</option>';

            books.forEach(book => {
                const row = document.createElement('tr');
                row.setAttribute('data-id', book.id);

                const isBorrowed = book.state === 'Borrowed';

                row.innerHTML = `<td>${book.id}</td>
                                 <td>${book.title}</td>
                                 <td>${book.author}</td>
                                 <td>${book.publisher}</td>
                                 <td>${book.genre}</td>
                                 <td>${book.borrower}</td>
                                 <td>${book.borrowDate}</td>
                                 <td>${book.returnDate || ''}</td>
                                 <td>${book.state}</td>`;
                bookTable.appendChild(row);

                const option = document.createElement('option');
                option.value = book.id;
                option.textContent = `${book.id} - ${book.title}`;

                if (isBorrowed) {
                    returnBookSelect.appendChild(option);
                } else {
                    borrowBookSelect.appendChild(option);
                }
            });
        })
        .catch(err => {
            console.error('Failed to load books:', err);
        });
};


// Handle Borrow Form Submission
document.getElementById('borrowForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const bookId = document.getElementById('borrowBookId').value;
    const borrowerName = document.getElementById('borrowerName').value.trim();
    const borrowDate = document.getElementById('borrowDate').value;
    const userId = 1; // hardcoded user_id

    if (!bookId || !borrowerName || !borrowDate) {
        alert('Please fill in all fields.');
        return;
    }

    // Send the borrow request to the backend API
    fetch(`/api/book/${bookId}`, { // Updated URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            borrowerName: borrowerName,
            borrowDate: borrowDate,
            user_id: userId
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
            // Update the UI if borrow is successful
            alert(`Book ID ${bookId} has been successfully borrowed.`);
            const row = document.querySelector(`#book-table tr[data-id="${bookId}"]`);
            if (row) {
                row.cells[5].textContent = borrowerName;
                row.cells[6].textContent = borrowDate;
                row.cells[8].textContent = 'Borrowed';
            }
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error borrowing book:', error);
    });
});

// Handle Return Form Submission
document.getElementById('returnForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const bookId = document.getElementById('returnBookId').value;
    const returnDateInput = document.getElementById('returnDate').value;

    if (!bookId || !returnDateInput) {
        alert('Please fill in all fields.');
        return;
    }

    // Send the return request to the backend API
    fetch(`/api/return/${bookId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            returnDate: returnDateInput,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
            // Update the UI if return is successful
            alert(`Book ID ${bookId} has been successfully returned.`);
            const row = document.querySelector(`#book-table tr[data-id="${bookId}"]`);
            if (row) {
                row.cells[5].textContent = '';
                row.cells[6].textContent = '';
                row.cells[7].textContent = '';
                row.cells[8].textContent = 'Present';
            }
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error returning book:', error);
    });
});

// Clear borrowing data from localStorage
document.getElementById('clearDataBtn').addEventListener('click', function () {
    if (confirm('Are you sure you want to clear all borrowing data? This action cannot be undone.')) {
        localStorage.removeItem('borrowingData'); // Only remove borrowing data
        location.reload(); // Reload the page after clearing the data
    }
});
