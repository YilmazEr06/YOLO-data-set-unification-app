from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QFrame, QListWidget,
    QListWidgetItem, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from utils.styles import DIALOG_STYLE
from reader import reader
import os
import shutil


class DecoderThread(QThread):
    progress = pyqtSignal(int, str)  # İlerleme ve durum mesajı için sinyal
    finished = pyqtSignal(bool, str)  # Başarı durumu ve mesaj için sinyal
    
    def __init__(self, reader_instance, dataset_names):
        super().__init__()
        self.reader = reader_instance
        self.dataset_names = dataset_names
        
    def run(self):
        try:
            total_datasets = len(self.dataset_names)
            
            for i, dataset_name in enumerate(self.dataset_names):
                # Her veri seti başlangıcında ilerlemeyi güncelle
                base_progress = (i * 100) // total_datasets
                self.progress.emit(base_progress, f"İşleniyor: {dataset_name}")
                
                # YAML dosyasını kontrol et
                yaml_path = os.path.join("datasets", dataset_name, "data.yaml")
                if not os.path.exists(yaml_path):
                    self.finished.emit(False, f"{dataset_name} için YAML dosyası bulunamadı")
                    return
                
                # İşlem aşamalarını göster
                self.progress.emit(base_progress + 25, f"{dataset_name}: YAML okunuyor...")
                
                # Decode işlemini gerçekleştir
                result = self.reader.categorize_yolo11_datasets(dataset_name)
                if not result:
                    self.finished.emit(False, f"{dataset_name} için kategorilere ayırma işlemi başarısız oldu")
                    return
                
                # Bu veri seti için işlem tamamlandı
                next_progress = ((i + 1) * 100) // total_datasets
                self.progress.emit(next_progress, f"{dataset_name} tamamlandı")
            
            # Tüm işlemler başarılı
            self.progress.emit(100, "Tamamlandı")
            self.finished.emit(True, "Kategorilere ayırma işlemi tamamlandı!")
            
        except Exception as e:
            self.finished.emit(False, str(e))


class DecoderTab(QWidget):
    """Decoder sekmesi için ana sınıf"""
    
    def __init__(self):
        super().__init__()
        self.selected_folders = []
        self.reader = reader()
        self.decoder_thread = None
        self.decoded_datasets = set()  # Decode edilmiş veri setlerini tutacak set
        self.load_decoded_datasets()  # Daha önce decode edilmiş veri setlerini yükle
        self.init_ui()
        
    def init_ui(self):
        """Kullanıcı arayüzünü başlatır"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Başlık
        title = QLabel("Decoder")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title.setStyleSheet("color: #424242; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Açıklama
        description = QLabel("Veri setinizi kategorilere ayırın.")
        description.setStyleSheet("color: #757575; margin-bottom: 20px;")
        layout.addWidget(description)
        
        # Ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(line)
        
        # Veri seti listesi başlığı
        dataset_label = QLabel("Veri Setleri:")
        dataset_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(dataset_label)
        
        # Veri seti listesi
        self.dataset_list = QListWidget()
        self.dataset_list.setSelectionMode(QListWidget.ExtendedSelection)  # Çoklu seçim
        self.dataset_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: #FFFFFF;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #212121;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
        """)
        layout.addWidget(self.dataset_list)
        
        # Seçili veri seti sayısı
        self.selection_label = QLabel("Seçili: 0 veri seti")
        self.selection_label.setStyleSheet("color: #1976D2; font-size: 11px;")
        layout.addWidget(self.selection_label)
        
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
        
        # Decode butonu
        self.decode_btn = QPushButton("🔄 Decode Et")
        self.decode_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.decode_btn.setEnabled(False)
        
        # Önbellek temizleme butonu
        self.clear_cache_btn = QPushButton("🗑️ Önbelleği Temizle")
        self.clear_cache_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        
        # Buton container'ı
        button_container = QHBoxLayout()
        button_container.addWidget(self.clear_cache_btn)
        button_container.addStretch()
        button_container.addWidget(self.decode_btn)
        layout.addLayout(button_container)
        
        # Olayları bağla
        self.decode_btn.clicked.connect(self.decode_datasets)
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        self.dataset_list.itemSelectionChanged.connect(self.update_selection_label)
        
        self.setLayout(layout)
        
        # Veri setlerini listele
        self.load_datasets()
        
    def load_decoded_datasets(self):
        """Daha önce decode edilmiş veri setlerini kontrol eder"""
        output_path = "output"
        if os.path.exists(output_path):
            for folder in os.listdir(output_path):
                folder_path = os.path.join(output_path, folder)
                if os.path.isdir(folder_path):
                    self.decoded_datasets.add(folder)

    def load_datasets(self):
        """Veri setlerini listeler ve decode edilmiş olanları işaretler"""
        self.dataset_list.clear()  # Listeyi temizle
        datasets_path = "datasets"
        if not os.path.exists(datasets_path):
            os.makedirs(datasets_path)
            return
            
        for dataset in os.listdir(datasets_path):
            dataset_path = os.path.join(datasets_path, dataset)
            if os.path.isdir(dataset_path) and os.path.exists(os.path.join(dataset_path, "data.yaml")):
                item = QListWidgetItem(dataset)
                if dataset in self.decoded_datasets:
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)  # Decode edilmiş veri setlerini devre dışı bırak
                    item.setForeground(QColor("#BDBDBD"))  # Gri renk ile göster
                    item.setToolTip("Bu veri seti zaten decode edilmiş")
                self.dataset_list.addItem(item)
                
    def update_selection_label(self):
        """Seçili veri seti sayısını günceller"""
        count = len(self.dataset_list.selectedItems())
        self.selection_label.setText(f"Seçili: {count} veri seti")
        self.decode_btn.setEnabled(count > 0)
        
    def decode_datasets(self):
        """Seçili veri setlerini decode eder"""
        selected_items = self.dataset_list.selectedItems()
        if not selected_items:
            return
            
        try:
            # UI'yi devre dışı bırak
            self.decode_btn.setEnabled(False)
            self.dataset_list.setEnabled(False)
            
            # Progress bar'ı hazırla
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.status_label.setText("Başlatılıyor...")
            
            # Seçili dataset isimlerini al
            dataset_names = [item.text() for item in selected_items]
            
            # Decoder thread'ini başlat
            self.decoder_thread = DecoderThread(self.reader, dataset_names)
            self.decoder_thread.progress.connect(self.update_progress)
            self.decoder_thread.finished.connect(self.handle_completion)
            self.decoder_thread.start()
            
            # Decode edilen veri setlerini listeye ekle
            for dataset in dataset_names:
                self.decoded_datasets.add(dataset)
            
        except Exception as e:
            self.handle_error(str(e))
            
    def update_progress(self, value, status):
        """İlerleme durumunu günceller"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
        # Arayüzün güncellenmesini zorla
        self.progress_bar.repaint()
        self.status_label.repaint()
        
    def handle_completion(self, success, message):
        """İşlem tamamlandığında çağrılır"""
        # UI'yi tekrar aktif et
        self.decode_btn.setEnabled(True)
        self.dataset_list.setEnabled(True)
        
        if success:
            self.status_label.setText("İşlem tamamlandı!")
            QMessageBox.information(self, "Başarılı", message)
        else:
            self.handle_error(message)
            
        # 2 saniye sonra progress bar'ı gizle
        QTimer.singleShot(2000, self.reset_ui)
        
    def handle_error(self, error_message):
        """Hata durumunu yönetir"""
        self.status_label.setText("Hata oluştu!")
        self.progress_bar.hide()
        self.decode_btn.setEnabled(True)
        self.dataset_list.setEnabled(True)
        QMessageBox.critical(self, "Hata", error_message)
        
    def reset_ui(self):
        """UI elemanlarını sıfırlar"""
        self.progress_bar.hide()
        self.status_label.setText("Hazır")
        self.progress_bar.setValue(0)
        
        # Veri setlerini listele
        self.load_datasets()
        
    def clear_cache(self):
        """Önbelleği temizler (output klasörünü siler)"""
        reply = QMessageBox.question(
            self,
            'Önbellek Temizleme',
            'Önbellek (output klasörü) silinecek. Bu işlem geri alınamaz. Devam etmek istiyor musunuz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                output_path = "output"
                if os.path.exists(output_path):
                    shutil.rmtree(output_path)
                    self.decoded_datasets.clear()  # Decode edilmiş veri setleri listesini temizle
                    self.load_datasets()  # Listeyi yenile
                    QMessageBox.information(self, "Başarılı", "Önbellek başarıyla temizlendi.")
                else:
                    QMessageBox.information(self, "Bilgi", "Temizlenecek önbellek bulunamadı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Önbellek temizlenirken bir hata oluştu: {str(e)}") 