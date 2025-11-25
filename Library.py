import os
from datetime import datetime

# --- Constants ---
BOOK_CATALOG_FILE = "books.txt"
ISSUED_RECORDS_FILE = "issued_books.txt"

# --- 1. Class and Data Structures (Concept: Class, List, Set, Dictionary) ---

class Library:
    """Manages the library's book catalog and issue records."""
    def __init__(self):
        # A list to store all available books (catalog)
        # Format: [{'id': 'B101', 'title': 'Python Guide', 'author': 'G.V.'}, ...]
        self.catalog = self._load_catalog()

        # A set for quick checking of available book IDs (Concept: Set)
        self.available_book_ids = {book['id'] for book in self.catalog}

        # A dictionary to map student IDs to a set of issued book IDs (Concept: Dictionary)
        # Format: {'S101': {'B105', 'B201'}, 'S102': {'B300'}, ...}
        self.issued_records = self._load_issued_records()


    # --- Internal File Handlers ---

    def _load_catalog(self):
        """Loads the book catalog from books.txt."""
        catalog = []
        if not os.path.exists(BOOK_CATALOG_FILE):
            return catalog
        try:
            with open(BOOK_CATALOG_FILE, 'r') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 3:
                        catalog.append({
                            'id': parts[0].strip(),
                            'title': parts[1].strip(),
                            'author': parts[2].strip()
                        })
        except IOError:
            print(f"Error loading {BOOK_CATALOG_FILE}.")
        return catalog

    def _save_catalog(self):
        """Saves the book catalog to books.txt."""
        try:
            with open(BOOK_CATALOG_FILE, 'w') as f:
                for book in self.catalog:
                    f.write(f"{book['id']}|{book['title']}|{book['author']}\n")
            print(f"Catalog saved to {BOOK_CATALOG_FILE}.")
        except IOError as e:
            print(f"Error saving catalog: {e}")

    def _load_issued_records(self):
        """Loads issued book records from issued_books.txt."""
        records = {}
        if not os.path.exists(ISSUED_RECORDS_FILE):
            return records
        try:
            with open(ISSUED_RECORDS_FILE, 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        student_id = parts[0].strip()
                        # Book IDs are stored as a comma-separated string, loaded into a Set
                        book_ids = set(parts[1].split(','))
                        records[student_id] = book_ids
        except IOError:
            print(f"Error loading {ISSUED_RECORDS_FILE}.")
        return records

    def _save_issued_records(self):
        """Stores the issued book data in file (issued_books.txt)."""
        try:
            with open(ISSUED_RECORDS_FILE, 'w') as f:
                for student_id, book_ids in self.issued_records.items():
                    # Save the set of book IDs as a comma-separated string
                    f.write(f"{student_id}: {','.join(book_ids)}\n")
            print(f"Issued records saved to {ISSUED_RECORDS_FILE}.")
        except IOError as e:
            print(f"Error saving issued records: {e}")

    # --- 2. Feature Implementation ---

    def add_book(self):
        """Feature: Add Book"""
        print("\n--- Add New Book ---")
        while True:
            book_id = input("Enter Book ID (e.g., B101): ").strip().upper()
            if book_id in self.available_book_ids:
                print(f"Error: Book ID {book_id} already exists. Use a unique ID.")
            else:
                break
        
        title = input("Enter Book Title: ").strip().title()
        author = input("Enter Author Name: ").strip().title()

        new_book = {'id': book_id, 'title': title, 'author': author}
        self.catalog.append(new_book)
        self.available_book_ids.add(book_id)
        
        print(f"Book '{title}' by {author} added successfully.")
        self._save_catalog()

    def display_available_books(self):
        """Feature: Display available Book"""
        print("\n--- Available Book Catalog ---")
        if not self.catalog:
            print("The library catalog is empty.")
            return

        # Filter the catalog based on what's NOT in the issued records
        issued_book_ids = set().union(*self.issued_records.values())
        
        available_books = [
            book for book in self.catalog 
            if book['id'] not in issued_book_ids
        ]

        if not available_books:
            print("All books are currently issued.")
            return

        print(f"Total books available: {len(available_books)}")
        for i, book in enumerate(available_books, 1):
            print(f"{i}. ID: {book['id']} | Title: {book['title']} | Author: {book['author']}")

    # --- 3. Methods: Borrow & return books ---

    def issue_book(self):
        """Feature: Return & Issue Book (Issue Part)"""
        print("\n--- Issue Book ---")
        student_id = input("Enter Student ID: ").strip().upper()
        book_id = input("Enter Book ID to issue: ").strip().upper()

        # Error handling (If book is not available)
        book_exists = any(book['id'] == book_id for book in self.catalog)
        if not book_exists:
            print(f"**Error**: Book ID {book_id} does not exist in the catalog.")
            return

        # Check if book is already issued
        is_issued = False
        for issued_set in self.issued_records.values():
            if book_id in issued_set:
                is_issued = True
                break
        
        if is_issued:
            print(f"**Error**: Book ID {book_id} is already issued.")
            # We could add logic here to display *who* has the book if needed
            return

        # Issue the book
        # Concept: Dictionary for Students, Book Mapping
        if student_id not in self.issued_records:
            self.issued_records[student_id] = set()
            
        self.issued_records[student_id].add(book_id)
        
        print(f"Book {book_id} successfully issued to Student {student_id}.")
        self._save_issued_records()


    def return_book(self):
        """Feature: Return & Issue Book (Return Part)"""
        print("\n--- Return Book ---")
        student_id = input("Enter Student ID: ").strip().upper()
        book_id = input("Enter Book ID to return: ").strip().upper()

        if student_id not in self.issued_records:
            print(f"**Error**: Student ID {student_id} has no outstanding issued books.")
            return

        if book_id in self.issued_records[student_id]:
            # Remove the book ID from the student's set
            self.issued_records[student_id].remove(book_id)

            # Clean up the student entry if their set is now empty
            if not self.issued_records[student_id]:
                del self.issued_records[student_id]
                
            print(f"Book {book_id} successfully returned by Student {student_id}.")
            self._save_issued_records()
        else:
            print(f"**Error**: Book ID {book_id} was not issued to Student {student_id}.")


# --- 4. Main Program Loop ---

def main():
    """Main function to run the Library Management System."""
    print("--- 📖 Welcome to the Library Management System 📖 ---")
    library = Library()

    while True:
        print("\n--- Main Menu ---")
        print("1. Add Book")
        print("2. Issue Book (Borrow)")
        print("3. Return Book")
        print("4. Display Available Books")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            library.add_book()
        elif choice == '2':
            library.issue_book()
        elif choice == '3':
            library.return_book()
        elif choice == '4':
            library.display_available_books()
        elif choice == '5':
            print("Exiting Library Management System. Have a great day!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

# --- Execute Main Function ---
if __name__ == "__main__":
    main()