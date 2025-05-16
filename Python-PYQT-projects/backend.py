import logging
import sys
from datetime import datetime, timedelta
from collections import deque, defaultdict
import difflib

# ======= Helper functions for nicer menus =======
def display_auth_menu():
    print("\n" + "-" * 50)
    print("📖  Welcome to the Library CLI  📖")
    print("-" * 50)
    print("[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-" * 50)

def display_main_menu(user_name: str):
    print("\n" + "=" * 60)
    print(f"👤  Logged in as: {user_name}")
    print("📚  Library Management System  📚")
    print("=" * 60)
    print("[1]  List all available books")
    print("[2]  Add a new book")
    print("[3]  Lend a book")
    print("[4]  Return a book")
    print("[5]  Search for a book")
    print("[6]  Reserve a book")
    print("[7]  Filter books by genre")
    print("[8]  Logout")
    print("[9]  Exit")
    print("-" * 60)

# ========== Custom Exceptions ==========
class BookNotFoundError(Exception):
    """When a requested book isn’t found in library"""
    pass

class BookNotAvailableError(Exception):
    """When no copies are available to lend"""
    pass

class UserLimitExceededError(Exception):
    """When a user tries to borrow more than allowed"""
    pass

class ReservationError(Exception):
    """Book reservation or queue related errors"""
    pass

# ========== Domain Classes ==========
class Book:
    def __init__(self, title: str, author: str, isbn: str, genre: str, total_copies: int = 1):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.total_copies = total_copies
        self.available_copies = total_copies

    def __repr__(self):
        return (f"{self.title} by {self.author} "
                f"(ISBN: {self.isbn}) - {self.available_copies}/{self.total_copies} available")

class eBook(Book):
    def __init__(self, title: str, author: str, isbn: str, genre: str, download_size_mb: float):
        super().__init__(title, author, isbn, genre, total_copies=1)
        self.download_size_mb = download_size_mb

# ========== Library Classes ==========
class Library:
    def __init__(self):
        self._books = {}            # isbn -> Book
        self._reservations = defaultdict(deque)  # isbn -> queue of user_ids

    def add_book(self, book: Book, count: int = 1):
        if book.isbn in self._books:
            existing = self._books[book.isbn]
            existing.total_copies += count
            existing.available_copies += count
        else:
            book.total_copies = count
            book.available_copies = count
            self._books[book.isbn] = book
        logging.info(f"ADD_BOOK: {book.title} x{count}")

    def remove_book(self, isbn: str, count: int = 1):
        if isbn not in self._books:
            raise BookNotFoundError("Book not found in library")
        book = self._books[isbn]
        if count > book.available_copies:
            raise BookNotAvailableError("Cannot remove more copies than available")
        book.total_copies -= count
        book.available_copies -= count
        if book.total_copies <= 0:
            del self._books[isbn]
        logging.info(f"REMOVE_BOOK: {isbn} x{count}")

    def lend_book(self, isbn: str, user_id: str):
        if isbn not in self._books:
            raise BookNotFoundError("Book not found in library")
        book = self._books[isbn]
        if book.available_copies <= 0:
            raise BookNotAvailableError("Book currently not available")
        book.available_copies -= 1
        due_date = datetime.now() + timedelta(days=14)
        logging.info(f"LEND_BOOK: {isbn} to {user_id}, due {due_date.date()}")
        return due_date

    def return_book(self, isbn: str, user_obj, return_date: datetime = None):
        if isbn not in self._books:
            raise BookNotFoundError("Book not found in library")
        book = self._books[isbn]
        book.available_copies += 1

        if return_date:
            due = user_obj.borrowed_books.get(isbn)
            if due and return_date.date() > due.date():
                days_late = (return_date.date() - due.date()).days
                fine = days_late * 1  # $1 per day
                print(f"You have a fine of ${fine} for late return.")

        if self._reservations[isbn]:
            next_user = self._reservations[isbn].popleft()
            print(f"Notification: {next_user}, your reserved book '{book.title}' is now available.")
            logging.info(f"RESERVATION_NOTIFY: {isbn} to {next_user}")

        logging.info(f"RETURN_BOOK: {isbn} by {user_obj.user_id}")

    def __iter__(self):
        self._iter_list = [b for b in self._books.values() if b.available_copies > 0]
        self._idx = 0
        return self

    def __next__(self):
        if self._idx >= len(self._iter_list):
            raise StopIteration
        book = self._iter_list[self._idx]
        self._idx += 1
        return book

    def books_by_author(self, author_name: str):
        for book in self._books.values():
            if book.author.lower() == author_name.lower():
                yield book

    def search_by_title(self, title: str):
        matches = [b for b in self._books.values() if title.lower() in b.title.lower()]
        if matches:
            return matches
        titles = [b.title for b in self._books.values()]
        return difflib.get_close_matches(title, titles)

    def search_by_author(self, author: str):
        return [b for b in self._books.values() if author.lower() in b.author.lower()]

    def search_by_isbn(self, isbn: str):
        return self._books.get(isbn)

    def filter_by_genre(self):
        genres = defaultdict(list)
        for b in self._books.values():
            if b.available_copies > 0:
                genres[b.genre].append(b)
        return genres

    def reserve_book(self, isbn: str, user_id: str):
        if isbn not in self._books:
            raise BookNotFoundError("Book not found in library")
        book = self._books[isbn]
        if book.available_copies > 0:
            raise ReservationError("Book is available; no need to reserve")
        self._reservations[isbn].append(user_id)
        logging.info(f"RESERVE_BOOK: {isbn} by {user_id}")

class DigitalLibrary(Library):
    def add_ebook(self, ebook: eBook):
        self.add_book(ebook, count=1)
        logging.info(f"ADD_EBOOK: {ebook.title}")

# ========== User Management ==========
default_borrow_limit = 5

class User:
    def __init__(self, user_id: str, name: str, password: str):
        self.user_id = user_id
        self.name = name
        self._password = password
        self.borrowed_books = {}    # isbn -> due_date
        self.reserved_books = set()

    def verify_password(self, password: str) -> bool:
        return password == self._password

class LibrarySystem:
    def __init__(self):
        # hide INFO logs from console
        logging.basicConfig(level=logging.WARNING,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.library = Library()
        self.dlibrary = DigitalLibrary()
        self.users = {}
        self.current_user = None

    def register_user(self, user_id, name, password):
        if user_id in self.users:
            print("User ID already exists.")
            return
        self.users[user_id] = User(user_id, name, password)
        print(f"User '{name}' registered successfully.")

    def login(self, user_id, password):
        user = self.users.get(user_id)
        if not user or not user.verify_password(password):
            print("Invalid credentials.")
            return False
        self.current_user = user
        print(f"Welcome, {user.name}!")
        return True

    def require_login(func):
        def wrapper(self, *args, **kwargs):
            if not self.current_user:
                print("Please login first.")
                return
            return func(self, *args, **kwargs)
        return wrapper

    @require_login
    def list_books(self):
        print("\nAvailable Books:")
        for idx, book in enumerate(self.library, start=1):
            print(f"{idx}. {book}")

    @require_login
    def add_book(self):
        print("\n-- Add New Book --")
        title = input("Title: ")
        author = input("Author: ")
        isbn = input("ISBN: ")
        genre = input("Genre: ")
        count = int(input("Number of copies: "))
        b = Book(title, author, isbn, genre, total_copies=count)
        self.library.add_book(b, count)
        print(f"Added '{title}' ({count} copies).")

    @require_login
    def lend_book(self):
        isbn = input("Enter ISBN to lend: ")
        try:
            if len(self.current_user.borrowed_books) >= default_borrow_limit:
                raise UserLimitExceededError("You have reached your borrow limit.")
            due = self.library.lend_book(isbn, self.current_user.user_id)
            self.current_user.borrowed_books[isbn] = due
            print(f"Book lent successfully. Due on {due.date()}.")
        except Exception as e:
            print(f"Error: {e}")

    @require_login
    def return_book(self):
        isbn = input("Enter ISBN to return: ")
        try:
            if isbn not in self.current_user.borrowed_books:
                print("You did not borrow this book.")
                return
            self.library.return_book(isbn, self.current_user, return_date=datetime.now())
            del self.current_user.borrowed_books[isbn]
            print("Book returned successfully.")
        except Exception as e:
            print(f"Error: {e}")

    @require_login
    def search_books(self):
        by = input("Search by (title/author/isbn): ").strip().lower()
        term = input("Enter search term: ").strip()
        if by == 'title':
            results = self.library.search_by_title(term)
        elif by == 'author':
            results = self.library.search_by_author(term)
        elif by == 'isbn':
            book = self.library.search_by_isbn(term)
            results = [book] if book else []
        else:
            print("Invalid search type.")
            return
        print("\nSearch Results:")
        if not results:
            print("No results found.")
        else:
            for b in results:
                print(b)

    @require_login
    def reserve_book(self):
        isbn = input("Enter ISBN to reserve: ")
        try:
            self.library.reserve_book(isbn, self.current_user.user_id)
            self.current_user.reserved_books.add(isbn)
            print("Book reserved successfully.")
        except Exception as e:
            print(f"Error: {e}")

    @require_login
    def filter_by_genre(self):
        genres = self.library.filter_by_genre()
        for genre, books in genres.items():
            print(f"\nGenre: {genre}")
            for b in books:
                print(f" - {b}")

    def logout(self):
        if self.current_user:
            print(f"Goodbye, {self.current_user.name}.")
        self.current_user = None

    def exit(self):
        print("Exiting system. Goodbye!")
        sys.exit(0)

    def seed_library(self):
        books_data = [
            ("To Kill a Mockingbird", "Harper Lee", "9780061120084", "Classic Fiction"),
            ("1984", "George Orwell", "9780451524935", "Dystopian Fiction"),
            ("Pride and Prejudice", "Jane Austen", "9780141199078", "Classic Romance"),
            ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", "Classic Fiction"),
            ("Moby-Dick", "Herman Melville", "9781503280786", "Adventure Fiction"),
            ("War and Peace", "Leo Tolstoy", "9780199232765", "Historical Fiction"),
            ("The Catcher in the Rye", "J.D. Salinger", "9780316769488", "Literary Fiction"),
            ("The Hobbit", "J.R.R. Tolkien", "9780547928227", "Fantasy"),
            ("Fahrenheit 451", "Ray Bradbury", "9781451673319", "Dystopian Fiction"),
            ("Brave New World", "Aldous Huxley", "9780060850524", "Dystopian Fiction"),
        ]
        for title, author, isbn, genre in books_data:
            b = Book(title, author, isbn, genre, total_copies=1)
            self.library.add_book(b, count=1)

    def manage_state(self):
        """Main state machine: show auth menu or main menu based on login state."""
        while True:
            if not self.current_user:
                display_auth_menu()
                choice = input("👉 Choose an option: ").strip()
                if choice == '1':
                    uid = input("   • User ID: ").strip()
                    name = input("   • Name: ").strip()
                    pw = input("   • Password: ").strip()
                    self.register_user(uid, name, pw)
                elif choice == '2':
                    uid = input("   • User ID: ").strip()
                    pw = input("   • Password: ").strip()
                    self.login(uid, pw)
                elif choice == '3':
                    self.exit()
                else:
                    print("❗ Invalid option, please enter 1, 2 or 3.")
            else:
                display_main_menu(self.current_user.name)
                action = input("👉 Select action [1–9]: ").strip()
                if action == '1':
                    self.list_books()
                elif action == '2':
                    self.add_book()
                elif action == '3':
                    self.lend_book()
                elif action == '4':
                    self.return_book()
                elif action == '5':
                    self.search_books()
                elif action == '6':
                    self.reserve_book()
                elif action == '7':
                    self.filter_by_genre()
                elif action == '8':
                    self.logout()
                elif action == '9':
                    self.exit()
                else:
                    print("❗ Invalid option, please enter a number from 1 to 9.")

# ========== Entry Point ==========
if __name__ == "__main__":
    system = LibrarySystem()
    system.seed_library()
    system.manage_state()
