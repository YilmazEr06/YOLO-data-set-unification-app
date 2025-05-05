import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QFrame, QLabel, QProgressBar, QDialog, QVBoxLayout,
    QSpinBox, QFormLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from dialogs.add_dialog import AddDialog
from dialogs.edit_dialog import EditDialog
from utils.ui_utils import show_info
from dataset_creator import creator
from reader import reader


class StatisticsDialog(QDialog):
    def __init__(self, category_names, counts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kategori İstatistikleri")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Kategorilere Göre Örnek Sayıları")
        title.setFont(QFont('Segoe UI', 12, QFont.Bold))
        title.setStyleSheet("color: #1976D2; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E0E0E0; margin: 10px 0;")
        layout.addWidget(line)
        
        # Kategori istatistikleri
        for category, count in zip(category_names, counts):
            stat_label = QLabel(f"{category}: {count} örnek")
            stat_label.setStyleSheet("""
                QLabel {
                    background-color: #E3F2FD;
                    padding: 8px;
                    border-radius: 4px;
                    margin: 2px 0;
                }
            """)
            layout.addWidget(stat_label)
        
        # Toplam
        total = sum(counts)
        total_label = QLabel(f"\nToplam: {total} örnek")
        total_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
        total_label.setStyleSheet("color: #1976D2; margin-top: 10px;")
        layout.addWidget(total_label)
        
        self.setLayout(layout)


class CreatorThread(QThread):
    progress = pyqtSignal(int, str)  # İlerleme ve durum mesajı için sinyal
    finished = pyqtSignal(bool, str, list, list)  # success, message, category_names, counts
    
    def __init__(self, selected_folders_list, category_names, max_images, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        super().__init__()
        self.creator = creator()
        self.reader = reader()
        self.selected_folders_list = selected_folders_list
        self.category_names = category_names
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.max_images = max_images
        
    def run(self):
        try:
            self.progress.emit(10, "Veri seti oluşturuluyor...")
            
            # Veri seti oluşturma işlemini başlat
            result = self.creator.create_dataset(
                self.selected_folders_list,
                self.category_names,
                self.train_ratio,
                self.val_ratio,
                self.test_ratio,
                self.max_images
            )
            
            if result:
                self.progress.emit(80, "Örnek sayıları hesaplanıyor...")
                # Örnek sayılarını hesapla
                counts = self.reader.count_yolo11_datasets("output_dataset")
                
                self.progress.emit(100, "Tamamlandı")
                self.finished.emit(True, "Veri seti başarıyla oluşturuldu!", self.category_names, counts)
            else:
                self.finished.emit(False, "Veri seti oluşturulurken bir hata oluştu.", [], [])
                
        except Exception as e:
            self.finished.emit(False, str(e), [], [])


class DatasetCreatorTab(QWidget):
    """Dataset Creator sekmesi için ana sınıf"""
    
    def __init__(self):
        super().__init__()
        self.creator_thread = None
        self.init_ui()
        
    def init_ui(self):
        """Kullanıcı arayüzünü başlatır"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Başlık
        title = QLabel("Dataset Creator")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title.setStyleSheet("color: #424242; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Açıklama
        description = QLabel("Veri setinizi oluşturmak için kategoriler ekleyin ve düzenleyin.")
        description.setStyleSheet("color: #757575; margin-bottom: 20px;")
        layout.addWidget(description)
        
        # Ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(line)
        
        # Tablo widget'ı
        self.dataset_table = QTableWidget(0, 3)
        self.dataset_table.setHorizontalHeaderLabels(["Kategori", "Dosyalar", "Toplam Görsel"])
        self.dataset_table.horizontalHeader().setStretchLastSection(True)
        self.dataset_table.setAlternatingRowColors(True)
        self.dataset_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F5F5F5;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)
        layout.addWidget(self.dataset_table)
        
        # Ayarlar bölümü
        settings_frame = QFrame()
        settings_frame.setFrameShape(QFrame.StyledPanel)
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        settings_layout = QFormLayout()
        
        # Maksimum görsel sayısı ayarı
        self.max_images_spin = QSpinBox()
        self.max_images_spin.setMinimum(100)
        self.max_images_spin.setMaximum(100000)
        self.max_images_spin.setValue(5000)
        self.max_images_spin.setSingleStep(100)
        self.max_images_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background: white;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
            }
        """)
        settings_layout.addRow("Kategori Başına Maksimum Görsel:", self.max_images_spin)
        settings_frame.setLayout(settings_layout)
        
        # Ayarlar bölümünü ana düzene ekle
        layout.addWidget(settings_frame)
        
        # Buton düzeni
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Butonları oluştur
        self.add_button = QPushButton("+ Kategori Ekle")
        self.edit_button = QPushButton("✎ Düzenle")
        self.create_dataset_button = QPushButton("⚡ Veri Kümesi Oluştur")
        
        # Buton stilleri
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFA000;
            }
        """)
        
        self.create_dataset_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        
        self.create_dataset_button.setEnabled(False)
        
        # Buton olaylarını bağla
        self.add_button.clicked.connect(self.show_add_dialog)
        self.edit_button.clicked.connect(self.show_edit_dialog)
        self.create_dataset_button.clicked.connect(self.create_dataset)
        
        # Butonları düzene ekle
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addStretch()
        button_layout.addWidget(self.create_dataset_button)
        
        layout.addLayout(button_layout)
        
        # Progress bar ve durum etiketi
        self.status_label = QLabel("Hazır")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #757575;
                font-size: 12px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                text-align: center;
                background-color: #F5F5F5;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
    def show_add_dialog(self):
        """Yeni kategori ekleme dialogunu gösterir"""
        dialog = AddDialog(self)
        if dialog.exec_() == AddDialog.Accepted:
            name = dialog.name_input.text().strip()
            files = dialog.get_selected_files()
            total_images = self._calculate_total_images(files)
            
            row_position = self.dataset_table.rowCount()
            self.dataset_table.insertRow(row_position)
            self.dataset_table.setItem(row_position, 0, QTableWidgetItem(name))
            self.dataset_table.setItem(row_position, 1, QTableWidgetItem(", ".join([os.path.basename(f) for f in files])))
            self.dataset_table.setItem(row_position, 2, QTableWidgetItem(str(total_images)))
            
            self.create_dataset_button.setEnabled(True)
            
    def show_edit_dialog(self):
        """Seçili kategoriyi düzenleme dialogunu gösterir"""
        row = self.dataset_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir kategori seçin.")
            return
            
        name = self.dataset_table.item(row, 0).text()
        files = [os.path.join("output", f.strip()) for f in self.dataset_table.item(row, 1).text().split(",")]
        
        dialog = EditDialog(name, files, self)
        if dialog.exec_() == EditDialog.Accepted:
            new_name = dialog.name_input.text().strip()
            new_files = dialog.get_selected_files()
            total_images = self._calculate_total_images(new_files)
            
            self.dataset_table.setItem(row, 0, QTableWidgetItem(new_name))
            self.dataset_table.setItem(row, 1, QTableWidgetItem(", ".join([os.path.basename(f) for f in new_files])))
            self.dataset_table.setItem(row, 2, QTableWidgetItem(str(total_images)))
            
    def create_dataset(self):
        """Veri kümesi oluşturma işlemini başlatır"""
        try:
            # Kategori ve dosya bilgilerini topla
            category_names = []
            selected_folders_list = []
            
            for row in range(self.dataset_table.rowCount()):
                category_name = self.dataset_table.item(row, 0).text()
                folders = [f.strip() for f in self.dataset_table.item(row, 1).text().split(",")]
                
                category_names.append(category_name)
                selected_folders_list.append(folders)
            
            if not category_names:
                QMessageBox.warning(self, "Uyarı", "Lütfen en az bir kategori ekleyin.")
                return
                
            # UI'yi devre dışı bırak
            self.setEnabled(False)
            
            # Progress bar'ı hazırla
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.status_label.setText("Başlatılıyor...")
            
            # Creator thread'ini başlat
            max_images = self.max_images_spin.value()
            self.creator_thread = CreatorThread(selected_folders_list, category_names, max_images)
            self.creator_thread.progress.connect(self.update_progress)
            self.creator_thread.finished.connect(self.handle_completion)
            self.creator_thread.start()
            
        except Exception as e:
            self.handle_error(str(e))
            
    def update_progress(self, value, status):
        """İlerleme durumunu günceller"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
        # Arayüzün güncellenmesini zorla
        self.progress_bar.repaint()
        self.status_label.repaint()
        
    def handle_completion(self, success, message, category_names, counts):
        """İşlem tamamlandığında çağrılır"""
        # UI'yi tekrar aktif et
        self.setEnabled(True)
        
        if success:
            self.status_label.setText("İşlem tamamlandı!")
            # İstatistik dialogunu göster
            dialog = StatisticsDialog(category_names, counts, self)
            dialog.exec_()
        else:
            self.handle_error(message)
            
        # Progress bar'ı gizle
        self.progress_bar.hide()
        self.status_label.setText("Hazır")
        
    def handle_error(self, error_message):
        """Hata durumunu yönetir"""
        self.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText("Hata oluştu!")
        QMessageBox.critical(self, "Hata", error_message)
        
    def _calculate_total_images(self, files):
        """Verilen dosya yollarındaki toplam görsel sayısını hesaplar"""
        total_images = 0
        for path in files:
            image_dir = os.path.join(path, "images")
            if os.path.exists(image_dir):
                total_images += len(os.listdir(image_dir))
        return total_images 