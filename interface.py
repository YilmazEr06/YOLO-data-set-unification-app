import os
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QTabWidget, QFormLayout, QTableWidget,
    QTableWidgetItem, QDialog, QListWidget, QDialogButtonBox, QMessageBox,
    QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from tabs.dataset_creator_tab import DatasetCreatorTab
from tabs.decoder_tab import DecoderTab
from utils.styles import MAIN_WINDOW_STYLE


class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kategori Ekle")
        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Kategori Adı:"))
        layout.addWidget(self.name_input)

        self.files_list = QListWidget()
        self.load_files()
        layout.addWidget(QLabel("Dosyalar:"))
        layout.addWidget(self.files_list)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def load_files(self):
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
        selected_files = []
        for item in self.files_list.selectedItems():
            match = re.match(r"(.+?)\s+\(\d+\)", item.text())
            if match:
                folder_name = match.group(1)
                selected_files.append(os.path.join("output", folder_name))
        return selected_files


class EditDialog(QDialog):
    def __init__(self, name, files, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kategori Düzenle")
        layout = QVBoxLayout()

        self.name_input = QLineEdit(name)
        layout.addWidget(QLabel("Kategori Adı:"))
        layout.addWidget(self.name_input)

        self.files_list = QListWidget()
        self.load_files(files)
        layout.addWidget(QLabel("Dosyalar:"))
        layout.addWidget(self.files_list)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def load_files(self, selected_files):
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
                if os.path.join("output", folder) in selected_files:
                    item.setSelected(True)
                self.files_list.addItem(item)

    def get_selected_files(self):
        selected_files = []
        for item in self.files_list.selectedItems():
            match = re.match(r"(.+?)\s+\(\d+\)", item.text())
            if match:
                folder_name = match.group(1)
                selected_files.append(os.path.join("output", folder_name))
        return selected_files


class Interface(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Kullanıcı arayüzünü başlatır"""
        self.setWindowTitle("Dataset Manager")
        self.setMinimumSize(800, 600)  # Minimum pencere boyutu
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Ana düzen
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)  # Kenar boşlukları
        main_layout.setSpacing(10)  # Widget'lar arası boşluk
        
        # Başlık etiketi
        title_label = QLabel("Dataset Manager")
        title_label.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #1976D2; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # Ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E0E0E0;")
        main_layout.addWidget(line)
        
        # Sekme widget'ı
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                color: #616161;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #E0E0E0;
            }
        """)
        
        # Sekmeleri oluştur
        self.dataset_creator_tab = DatasetCreatorTab()
        self.decoder_tab = DecoderTab()
        
        # Sekmeleri ekle
        self.tabs.addTab(self.dataset_creator_tab, "Dataset Creator")
        self.tabs.addTab(self.decoder_tab, "Decoder")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def load_decoded_datasets(self):
        """Daha önce decode edilmiş veri setlerini kontrol eder"""
        output_path = "output"
        if os.path.exists(output_path):
            for folder in os.listdir(output_path):
                folder_path = os.path.join(output_path, folder)
                if os.path.isdir(folder_path):
                    self.decoded_datasets.add(folder)

    def clear_decoded_datasets(self):
        self.decoded_datasets.clear()
        self.load_datasets()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Uygulama genelinde font ayarı
    app.setFont(QFont('Segoe UI', 10))
    
    # Uygulama genelinde renk paleti
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor('#FFFFFF'))
    palette.setColor(QPalette.WindowText, QColor('#212121'))
    app.setPalette(palette)
    
    interface = Interface()
    interface.show()
    sys.exit(app.exec_())
