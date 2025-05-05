import os
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QListWidget, QDialogButtonBox,
    QListWidgetItem, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from utils.styles import DIALOG_STYLE


class EditDialog(QDialog):
    """Kategori düzenleme dialog sınıfı"""
    
    def __init__(self, name, files, parent=None):
        super().__init__(parent)
        self.initial_files = files  # Başlangıçtaki seçili dosyaları sakla
        self.init_ui(name)
        
    def init_ui(self, name):
        """Kullanıcı arayüzünü başlatır"""
        self.setWindowTitle("Kategori Düzenle")
        self.setStyleSheet(DIALOG_STYLE)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Kategori adı girişi
        name_label = QLabel("Kategori Adı:")
        name_label.setStyleSheet("font-weight: bold;")
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Kategori adını giriniz...")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        
        # Dosya listesi başlığı ve açıklama
        files_header = QHBoxLayout()
        files_label = QLabel("Dosyalar:")
        files_label.setStyleSheet("font-weight: bold;")
        files_header.addWidget(files_label)
        
        # Seçim işlemleri butonları
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Tümünü Seç")
        clear_all_btn = QPushButton("Seçimleri Temizle")
        restore_btn = QPushButton("Önceki Seçimleri Geri Yükle")
        
        # Buton stilleri
        button_style = """
            QPushButton {
                background-color: #F5F5F5;
                color: #424242;
                border: 1px solid #E0E0E0;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #EEEEEE;
                border-color: #BDBDBD;
            }
        """
        select_all_btn.setStyleSheet(button_style)
        clear_all_btn.setStyleSheet(button_style)
        restore_btn.setStyleSheet(button_style)
        
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(clear_all_btn)
        button_layout.addWidget(restore_btn)
        files_header.addLayout(button_layout)
        layout.addLayout(files_header)
        
        # Dosya listesi ve yardım metni
        help_text = QLabel("(Ctrl veya Shift tuşu ile seçim yapabilir veya seçimleri kaldırabilirsiniz)")
        help_text.setStyleSheet("color: #757575; font-size: 11px;")
        layout.addWidget(help_text)
        
        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.files_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.load_files()
        layout.addWidget(self.files_list)
        
        # Seçili dosya sayısı
        self.selection_label = QLabel()
        self.selection_label.setStyleSheet("color: #1976D2; font-size: 11px;")
        self.update_selection_label()
        layout.addWidget(self.selection_label)
        
        # Dialog butonları
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Buton olayları
        select_all_btn.clicked.connect(self.select_all_items)
        clear_all_btn.clicked.connect(self.clear_all_selections)
        restore_btn.clicked.connect(self.restore_initial_selection)
        
        # Pencere boyutunu ayarla
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
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
                item_text = f"{folder} ({image_count})"
                item = QListWidgetItem(item_text)
                
                # Önceden seçili olan dosyaları işaretle
                if os.path.join("output", folder) in self.initial_files:
                    item.setSelected(True)
                
                self.files_list.addItem(item)
        
        # İlk yüklemede arka plan renklerini güncelle
        self.update_background_colors()
                
    def get_selected_files(self):
        """Seçili dosyaların tam yollarını döndürür"""
        selected_files = []
        for item in self.files_list.selectedItems():
            match = re.match(r"(.+?)\s+\(\d+\)", item.text())
            if match:
                folder_name = match.group(1)
                selected_files.append(os.path.join("output", folder_name))
        return selected_files
        
    def select_all_items(self):
        """Tüm öğeleri seçer"""
        for i in range(self.files_list.count()):
            self.files_list.item(i).setSelected(True)
        self.update_background_colors()
        self.update_selection_label()
        
    def clear_all_selections(self):
        """Tüm seçimleri temizler"""
        for i in range(self.files_list.count()):
            self.files_list.item(i).setSelected(False)
        self.update_background_colors()
        self.update_selection_label()
        
    def restore_initial_selection(self):
        """Başlangıçtaki seçimleri geri yükler"""
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            match = re.match(r"(.+?)\s+\(\d+\)", item.text())
            if match:
                folder_name = match.group(1)
                full_path = os.path.join("output", folder_name)
                item.setSelected(full_path in self.initial_files)
        self.update_background_colors()
        self.update_selection_label()
        
    def on_selection_changed(self):
        """Seçim değiştiğinde arka plan renklerini günceller"""
        self.update_background_colors()
        self.update_selection_label()
        
    def update_background_colors(self):
        """Seçili öğelerin arka plan renklerini günceller"""
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            if item.isSelected():
                item.setBackground(QColor("#E3F2FD"))
            else:
                item.setBackground(QColor("#FFFFFF"))
        
    def update_selection_label(self):
        """Seçili dosya sayısını günceller"""
        count = len(self.files_list.selectedItems())
        total = self.files_list.count()
        self.selection_label.setText(f"Seçili: {count} / Toplam: {total} dosya") 