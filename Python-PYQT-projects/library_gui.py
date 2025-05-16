import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QDialog, QSpinBox, QComboBox, QHeaderView
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from backend import LibrarySystem, Book

# Common styles for widgets
def common_styles():
    return {
        'button': (
            "QPushButton { background-color: #0066CC; color: white; border-radius: 6px; padding: 8px; }"
            "QPushButton:hover { background-color: #005BB5; }"
            "QPushButton:pressed { background-color: #004C99; }"
        ),
        'lineedit': (
            "QLineEdit { border: 1px solid #ccc; border-radius: 4px; padding: 6px; }"
            "QLineEdit:focus { border-color: #0066CC; }"
        )
    }

class StyledButton(QPushButton):
    def __init__(self, text, width=120):
        super().__init__(text)
        self.setFixedWidth(width)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(common_styles()['button'])

class StyledLineEdit(QLineEdit):
    def __init__(self, placeholder='', width=200, password=False):
        super().__init__()
        self.setFixedWidth(width)
        self.setPlaceholderText(placeholder)
        if password:
            self.setEchoMode(QLineEdit.Password)
        self.setStyleSheet(common_styles()['lineedit'])

class LoginRegisterWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)

        title = QLabel("📖 Library Management System 📖")
        title.setFont(QFont('Helvetica', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Tabs
        tab_layout = QHBoxLayout()
        tab_layout.addStretch()
        self.login_tab = StyledButton("Login", 100)
        self.register_tab = StyledButton("Register", 100)
        tab_layout.addWidget(self.login_tab)
        tab_layout.addWidget(self.register_tab)
        tab_layout.addStretch()
        main_layout.addLayout(tab_layout)

        # Stack
        self.stack = QStackedWidget()
        self._create_login_form()
        self._create_register_form()
        main_layout.addWidget(self.stack)

        self.login_tab.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.register_tab.clicked.connect(lambda: self.stack.setCurrentIndex(1))

    def _create_login_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # User ID row
        row1 = QHBoxLayout()
        row1.addStretch()
        lbl_id = QLabel("User ID:")
        lbl_id.setFixedWidth(80)
        lbl_id.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.login_id = StyledLineEdit('Enter ID')
        row1.addWidget(lbl_id)
        row1.addWidget(self.login_id)
        row1.addStretch()
        layout.addLayout(row1)

        # Password row
        row2 = QHBoxLayout()
        row2.addStretch()
        lbl_pw = QLabel("Password:")
        lbl_pw.setFixedWidth(80)
        lbl_pw.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.login_pw = StyledLineEdit('Enter Password', password=True)
        row2.addWidget(lbl_pw)
        row2.addWidget(self.login_pw)
        row2.addStretch()
        layout.addLayout(row2)

        # Button row
        btn = StyledButton("Login", 120)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        btn.clicked.connect(self._handle_login)

        self.stack.addWidget(page)

    def _create_register_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # User ID row
        row1 = QHBoxLayout()
        row1.addStretch()
        lbl_id = QLabel("User ID:")
        lbl_id.setFixedWidth(80)
        lbl_id.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.reg_id = StyledLineEdit('New ID')
        row1.addWidget(lbl_id)
        row1.addWidget(self.reg_id)
        row1.addStretch()
        layout.addLayout(row1)

        # Name row
        row2 = QHBoxLayout()
        row2.addStretch()
        lbl_name = QLabel("Name:")
        lbl_name.setFixedWidth(80)
        lbl_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.reg_name = StyledLineEdit('Full Name')
        row2.addWidget(lbl_name)
        row2.addWidget(self.reg_name)
        row2.addStretch()
        layout.addLayout(row2)

        # Password row
        row3 = QHBoxLayout()
        row3.addStretch()
        lbl_pw = QLabel("Password:")
        lbl_pw.setFixedWidth(80)
        lbl_pw.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.reg_pw = StyledLineEdit('New Password', password=True)
        row3.addWidget(lbl_pw)
        row3.addWidget(self.reg_pw)
        row3.addStretch()
        layout.addLayout(row3)

        # Button row
        btn = StyledButton("Register", 120)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        btn.clicked.connect(self._handle_register)

        self.stack.addWidget(page)

    def _handle_login(self):
        if self.parent.system.login(self.login_id.text(), self.login_pw.text()):
            self.parent.show_main()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid user ID or password.")

    def _handle_register(self):
        self.parent.system.register_user(
            self.reg_id.text(), self.reg_name.text(), self.reg_pw.text()
        )
        QMessageBox.information(self, "Registered",
                                f"User '{self.reg_name.text()}' registered.")
        self.stack.setCurrentIndex(0)

class MainWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)

        # User label
        self.lbl_user = QLabel()
        self.lbl_user.setFont(QFont('Arial', 12))
        layout.addWidget(self.lbl_user)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        actions = {
            "List Books": self.list_books,
            "Add Book": self.add_book_dialog,
            "Lend Book": self.lend_book_dialog,
            "Return Book": self.return_book_dialog,
            "Search Books": self.search_books_dialog,
            "Reserve Book": self.reserve_book_dialog,
            "Filter Genre": self.filter_genre,
            "Logout": self.parent.logout
        }
        for name, func in actions.items():
            btn = StyledButton(name, width=110)
            btn.clicked.connect(func)
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        # Table view
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def refresh_user(self):
        user = self.parent.system.current_user
        self.lbl_user.setText(f"👤 Logged in as: {user.name}")
        self.list_books()

    def list_books(self):
        books = list(self.parent.system.library._books.values())
        self._populate_table(books)

    def add_book_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Add New Book")
        form = QVBoxLayout(dlg)

        # Reuse centered rows
        for label_text, widget in [
            ("Title:", StyledLineEdit('Title')),
            ("Author:", StyledLineEdit('Author')),
            ("ISBN:", StyledLineEdit('ISBN')),
            ("Genre:", StyledLineEdit('Genre'))
        ]:
            row = QHBoxLayout()
            row.addStretch()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(80)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(lbl)
            row.addWidget(widget)
            row.addStretch()
            form.addLayout(row)
            if label_text == "Title:": title = widget
            if label_text == "Author:": author = widget
            if label_text == "ISBN:": isbn = widget
            if label_text == "Genre:": genre = widget

        # Copies spinner
        count_row = QHBoxLayout()
        count_row.addStretch()
        lbl_count = QLabel("Copies:")
        lbl_count.setFixedWidth(80)
        lbl_count.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        count = QSpinBox()
        count.setMinimum(1)
        count_row.addWidget(lbl_count)
        count_row.addWidget(count)
        count_row.addStretch()
        form.addLayout(count_row)

        # Add button
        btn = StyledButton("Add", width=100)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        form.addLayout(btn_row)
        btn.clicked.connect(lambda: self._add_book(title, author, isbn, genre, count, dlg))

        dlg.exec_()

    def _add_book(self, title, author, isbn, genre, count, dlg):
        self.parent.system.library.add_book(
            Book(title.text(), author.text(), isbn.text(), genre.text(), count.value()),
            count.value()
        )
        QMessageBox.information(self, "Success", "Book added.")
        dlg.accept()
        self.list_books()

    def lend_book_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Lend Book")
        form = QVBoxLayout(dlg)

        # ISBN row
        row = QHBoxLayout()
        row.addStretch()
        lbl = QLabel("ISBN:")
        lbl.setFixedWidth(80)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        isbn = StyledLineEdit('ISBN')
        row.addWidget(lbl)
        row.addWidget(isbn)
        row.addStretch()
        form.addLayout(row)

        # Lend button
        btn = StyledButton("Lend", width=100)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        form.addLayout(btn_row)
        btn.clicked.connect(lambda: self._lend_book(isbn, dlg))

        dlg.exec_()

    def _lend_book(self, isbn_field, dlg):
        try:
            due = self.parent.system.library.lend_book(
                isbn_field.text(), self.parent.system.current_user.user_id
            )
            self.parent.system.current_user.borrowed_books[isbn_field.text()] = due
            QMessageBox.information(self, "Lent", f"Due on {due.date()}")
            dlg.accept()
            self.list_books()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def return_book_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Return Book")
        form = QVBoxLayout(dlg)

        # ISBN row
        row = QHBoxLayout()
        row.addStretch()
        lbl = QLabel("ISBN:")
        lbl.setFixedWidth(80)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        isbn = StyledLineEdit('ISBN')
        row.addWidget(lbl)
        row.addWidget(isbn)
        row.addStretch()
        form.addLayout(row)

        # Return button
        btn = StyledButton("Return", width=100)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        form.addLayout(btn_row)
        btn.clicked.connect(lambda: self._return_book(isbn, dlg))

        dlg.exec_()

    def _return_book(self, isbn_field, dlg):
        try:
            self.parent.system.library.return_book(
                isbn_field.text(), self.parent.system.current_user, datetime.now()
            )
            del self.parent.system.current_user.borrowed_books[isbn_field.text()]
            QMessageBox.information(self, "Returned", "Book returned.")
            dlg.accept()
            self.list_books()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def search_books_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Search Books")
        form = QVBoxLayout(dlg)

        # Search by row
        row1 = QHBoxLayout()
        row1.addStretch()
        lbl_by = QLabel("By:")
        lbl_by.setFixedWidth(80)
        lbl_by.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        combo = QComboBox()
        combo.addItems(["title", "author", "isbn"])
        row1.addWidget(lbl_by)
        row1.addWidget(combo)
        row1.addStretch()
        form.addLayout(row1)

        # Term row
        row2 = QHBoxLayout()
        row2.addStretch()
        lbl_term = QLabel("Term:")
        lbl_term.setFixedWidth(80)
        lbl_term.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        term = StyledLineEdit('Search term')
        row2.addWidget(lbl_term)
        row2.addWidget(term)
        row2.addStretch()
        form.addLayout(row2)

        # Search button
        btn = StyledButton("Search", width=100)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        form.addLayout(btn_row)
        btn.clicked.connect(lambda: self._search(combo.currentText(), term.text(), dlg))

        dlg.exec_()

    def _search(self, by, term, dlg):
        if by == 'title':
            results = self.parent.system.library.search_by_title(term)
        elif by == 'author':
            results = self.parent.system.library.search_by_author(term)
        else:
            book = self.parent.system.library.search_by_isbn(term)
            results = [book] if book else []
        dlg.accept()
        self._populate_table(results)

    def reserve_book_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Reserve Book")
        form = QVBoxLayout(dlg)

        # ISBN row
        row = QHBoxLayout()
        row.addStretch()
        lbl = QLabel("ISBN:")
        lbl.setFixedWidth(80)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        isbn = StyledLineEdit('ISBN')
        row.addWidget(lbl)
        row.addWidget(isbn)
        row.addStretch()
        form.addLayout(row)

        # Reserve button
        btn = StyledButton("Reserve", width=100)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        form.addLayout(btn_row)
        btn.clicked.connect(lambda: self._reserve(isbn, dlg))

        dlg.exec_()

    def _reserve(self, isbn_field, dlg):
        try:
            self.parent.system.library.reserve_book(
                isbn_field.text(), self.parent.system.current_user.user_id
            )
            self.parent.system.current_user.reserved_books.add(isbn_field.text())
            QMessageBox.information(self, "Reserved", "Book reserved.")
            dlg.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def filter_genre(self):
        genres = self.parent.system.library.filter_by_genre()
        items = []
        for g, books in genres.items():
            for b in books:
                items.append((g, b.title, b.author, b.isbn,
                              str(b.available_copies), str(b.total_copies)))
        self.table.clear()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Genre", "Title", "Author", "ISBN", "Avail", "Total"])
        self.table.setRowCount(len(items))
        for r, row in enumerate(items):
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(val))

    def _populate_table(self, book_list):
        self.table.clear()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Title", "Author", "ISBN", "Genre", "Avail/Total"])
        self.table.setRowCount(len(book_list))
        for r, b in enumerate(book_list):
            self.table.setItem(r, 0, QTableWidgetItem(b.title))
            self.table.setItem(r, 1, QTableWidgetItem(b.author))
            self.table.setItem(r, 2, QTableWidgetItem(b.isbn))
            self.table.setItem(r, 3, QTableWidgetItem(b.genre))
            self.table.setItem(r, 4, QTableWidgetItem(
                f"{b.available_copies}/{b.total_copies}"))

class LibraryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.system = LibrarySystem()
        self.system.seed_library()
        self.setWindowTitle("Library Management System")
        self.setWindowIcon(QIcon.fromTheme("book"))
        self.resize(800, 600)

        self.stack = QStackedWidget()
        self.login_widget = LoginRegisterWidget(self)
        self.main_widget = MainWidget(self)
        self.stack.addWidget(self.login_widget)
        self.stack.addWidget(self.main_widget)
        self.setCentralWidget(self.stack)

    def show_main(self):
        self.main_widget.refresh_user()
        self.stack.setCurrentWidget(self.main_widget)

    def logout(self):
        self.system.logout()
        self.stack.setCurrentWidget(self.login_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LibraryApp()
    window.show()
    sys.exit(app.exec_())
