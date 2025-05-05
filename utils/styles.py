from PyQt5.QtGui import QColor

# Ana renkler
PRIMARY_COLOR = "#2196F3"  # Mavi
SECONDARY_COLOR = "#FFC107"  # Amber
BACKGROUND_COLOR = "#FFFFFF"  # Beyaz
TEXT_COLOR = "#212121"  # Koyu gri
BORDER_COLOR = "#E0E0E0"  # Açık gri

# Stil tanımlamaları
MAIN_WINDOW_STYLE = """
QWidget {
    background-color: #FFFFFF;
    color: #212121;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:disabled {
    background-color: #BDBDBD;
}

QTableWidget {
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    gridline-color: #F5F5F5;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #E3F2FD;
    color: #212121;
}

QHeaderView::section {
    background-color: #F5F5F5;
    color: #616161;
    padding: 8px;
    border: none;
    border-right: 1px solid #E0E0E0;
    border-bottom: 1px solid #E0E0E0;
}

QLineEdit {
    padding: 8px;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    background-color: #FFFFFF;
}

QLineEdit:focus {
    border: 2px solid #2196F3;
}

QListWidget {
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    background-color: #FFFFFF;
}

QListWidget::item {
    padding: 8px;
}

QListWidget::item:selected {
    background-color: #E3F2FD;
    color: #212121;
}

QListWidget::item:hover {
    background-color: #F5F5F5;
}

QDialog {
    background-color: #FFFFFF;
}

QLabel {
    color: #424242;
}
"""

# Dialog penceresi stili
DIALOG_STYLE = """
QDialog {
    background-color: #FFFFFF;
}

QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QDialogButtonBox QPushButton[text="Cancel"] {
    background-color: #F5F5F5;
    color: #212121;
}

QDialogButtonBox QPushButton[text="Cancel"]:hover {
    background-color: #E0E0E0;
}
""" 