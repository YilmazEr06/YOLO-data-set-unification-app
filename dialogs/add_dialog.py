import os
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QListWidget, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from utils.styles import DIALOG_STYLE


class AddDialog(QDialog):
    """Yeni kategori ekleme dialog sınıfı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Kullanıcı arayüzünü başlatır"""
        self.setWindowTitle("Kategori Ekle")
        self.setStyleSheet(DIALOG_STYLE)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Kategori adı girişi
        name_label = QLabel("Kategori Adı:")
        name_label.setStyleSheet("font-weight: bold;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Kategori adını giriniz...")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        
        # Dosya listesi
        files_label = QLabel("Dosyalar: (Ctrl veya Shift tuşu ile çoklu seçim yapabilirsiniz)")
        files_label.setStyleSheet("font-weight: bold;")
        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QListWidget.ExtendedSelection)  # Çoklu seçim modunu aktifleştir
        self.load_files()
        layout.addWidget(files_label)
        layout.addWidget(self.files_list)
        
        # Dialog butonları
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Pencere boyutunu ayarla
        self.setMinimumWidth(400)
        self.setLayout(layout)
        
    def load_files(self):
        """Output klasöründeki dosyaları yükler"""
        output_path = "output"
        if not os.path.exists(output_path):
            return
            
        for folder in os.listdir(output_path):
            full_path = os.path.join(output_path, folder)
            images_path = os.path.join(full_path, "images")
            if os.path.isdir(full_path) and os.path.exists(images_path):
                image_count = len(os.listdir(images_path))
                item = f"{folder} ({image_count})"
                self.files_list.addItem(item)
                
    def get_selected_files(self):
        """Seçili dosyaların tam yollarını döndürür"""
        selected_files = []
        for item in self.files_list.selectedItems():
            match = re.match(r"(.+?)\s+\(\d+\)", item.text())
            if match:
                folder_name = match.group(1)
                selected_files.append(os.path.join("output", folder_name))
        return selected_files 