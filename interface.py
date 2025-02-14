from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QTabWidget, QListWidget, QComboBox, QDialog,
                           QLineEdit, QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox,QAbstractItemView, QProgressBar)
from PyQt5.QtCore import Qt
from decoder import Decoder
from reader import reader
import os
import shutil
from dataset_creator import create_dataset
from PyQt5.QtGui import QIntValidator
import re


class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add New Category')
        self.setFixedSize(300, 400)
        
        layout = QVBoxLayout()
        
        # Kategori ismi için etiket
        name_label = QLabel("Kategori İsmi:")
        layout.addWidget(name_label)
        
        # Kategori ismi için giriş alanı
        self.name_input = QLineEdit()
        self.name_input.textChanged.connect(self.check_inputs)  # Metin değişikliğini izle
        layout.addWidget(self.name_input)
        
        # Dosya listesi etiketi
        files_list_label = QLabel("Dosyaları Seç:")
        layout.addWidget(files_list_label)
        
        # Dosya listesi
        self.files_list = QListWidget()
        self.files_list.setMinimumHeight(200)  # Minimum yükseklik
        self.files_list.setSelectionMode(QListWidget.MultiSelection)
        self.files_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)
        layout.addWidget(self.files_list)
        
        # Output klasöründeki dosyaları listeye ekle
        output_path = os.path.abspath("output")  # Tam yolu al
        print(f"Output klasörünün tam yolu: {output_path}")
        print(f"Output klasörü var mı: {os.path.exists(output_path)}")
        if os.path.exists(output_path):
            
            files = os.listdir(output_path)
            print(f"Output klasöründeki dosyalar: {files}")
            for file in files:
                images_path = os.path.join(output_path, file, "images")  # images klasörünün yolu
                if os.path.exists(images_path):
                    image_files = os.listdir(images_path)  # images klasöründeki dosyaları listele
                    image_count = len(image_files)  # Nesne sayısını al
                    print(f"Images klasöründeki nesne sayısı: {image_count}")
                else:
                    print("Images klasörü bulunamadı!")

                
                item = QListWidgetItem(f"{file} ({image_count})" )
                self.files_list.addItem(item)
                print(f"Listeye eklenen: {file}")
        else:
            print("Output klasörü bulunamadı!")
            # Output klasörünü oluştur
            os.makedirs(output_path, exist_ok=True)
            print("Output klasörü oluşturuldu")
        
      
        
        # Seçilen dosya sayısını göstermek için etiket
        self.files_label = QLabel("Seçilen dosya: 0")
        layout.addWidget(self.files_label)
        
        # Liste seçim değişikliğini takip et
        self.files_list.itemSelectionChanged.connect(self.update_selection_count)
        
        # Onay ve İptal butonları
        buttons_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Okey")  # Buton adı değiştirildi
        self.ok_button.setEnabled(False)  # Başlangıçta devre dışı
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")  # Buton adı değiştirildi
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
    def check_inputs(self):
        # Hem kategori ismi hem de seçili dosya varsa butonu etkinleştir
        has_name = bool(self.name_input.text().strip())  # Boşlukları temizle
        has_selection = len(self.files_list.selectedItems()) > 0
        self.ok_button.setEnabled(has_name and has_selection)
        
    def update_selection_count(self):
        selected_count = len(self.files_list.selectedItems())
        self.files_label.setText(f"Seçilen dosya: {selected_count}")
        self.check_inputs()  # Seçim değiştiğinde de kontrol et
        
    def get_selected_files(self):
        return [os.path.join("output", item.text()) for item in self.files_list.selectedItems()]

class EditDialog(QDialog):
    def __init__(self, category_name, files, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Category')
        self.setFixedSize(300, 400)
        
        layout = QVBoxLayout()
        
        # Kategori ismi için etiket
        name_label = QLabel("Kategori İsmi:")
        layout.addWidget(name_label)
        
        # Kategori ismi için giriş alanı
        self.name_input = QLineEdit()
        self.name_input.setText(category_name)
        self.name_input.textChanged.connect(self.check_inputs)
        layout.addWidget(self.name_input)
        
        # Dosya listesi etiketi
        files_list_label = QLabel("Dosyaları Seç:")
        layout.addWidget(files_list_label)
        
        # Dosya listesi
        self.files_list = QListWidget()
        self.files_list.setMinimumHeight(200)
        self.files_list.setSelectionMode(QListWidget.MultiSelection)
        self.files_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)
        layout.addWidget(self.files_list)
        
        # Output klasöründeki dosyaları listeye ekle ve seçili olanları işaretle
        output_path = os.path.abspath("output")
        if os.path.exists(output_path):
            for file in os.listdir(output_path):
                item = QListWidgetItem(file)
                self.files_list.addItem(item)
                if file in files:  # Eğer dosya daha önce seçiliyse
                    item.setSelected(True)
        
        # Seçilen dosya sayısını göstermek için etiket
        self.files_label = QLabel(f"Seçilen dosya: {len(files)}")
        layout.addWidget(self.files_label)
        
        # Liste seçim değişikliğini takip et
        self.files_list.itemSelectionChanged.connect(self.update_selection_count)
        
        # Onay ve İptal butonları
        buttons_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Okey")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
    def check_inputs(self):
        has_name = bool(self.name_input.text().strip())
        has_selection = len(self.files_list.selectedItems()) > 0
        self.ok_button.setEnabled(has_name and has_selection)
        
    def update_selection_count(self):
        selected_count = len(self.files_list.selectedItems())
        self.files_label.setText(f"Seçilen dosya: {selected_count}")
        self.check_inputs()
        
    def get_selected_files(self):
        return [item.text() for item in self.files_list.selectedItems()]

class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.reader = reader()
        self.setWindowTitle("Dataset Manager")
        self.setGeometry(100, 100, 120, 400)  # Genişlik 100px, Yükseklik 400px
        
        self.decoder = Decoder()  # Decoder nesnesi eklendi
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        self.init_creator_tab()
        self.init_decoder_tab()
        
        self.tab_widget.addTab(self.creator_tab, "Dataset Creator")
        self.tab_widget.addTab(self.decoder_tab, "Decoder")

    def init_creator_tab(self):
        self.creator_tab = QWidget()  # Kategori sekmesi için widget oluştur
        layout = QVBoxLayout(self.creator_tab)  # Burada self.creator_tab kullanmalısınız
        
        # Liste widget'ı yerine tablo widget'ı oluştur
        self.dataset_table = QTableWidget()
        self.dataset_table.setColumnCount(3)  # Kolon sayısını 3'e düşür
        self.dataset_table.setHorizontalHeaderLabels(["Kategori", "Dosyalar", "Toplam"])  # Açıklama kolonunu kaldır
        
        # Tabloyu düzenlenemez yap
        self.dataset_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Tablo stilini ayarla
        self.dataset_table.setStyleSheet(""" 
            QTableWidget {
                border: 1px solid #ccc;
                gridline-color: #ccc;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ccc;
            }
        """)
        
        # Sütun genişliklerini ayarla
        header = self.dataset_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Toplam kolonu için genişlik ayarı
        
        layout.addWidget(self.dataset_table)
        
        # Oranlar için etiketler ve giriş alanları
        self.train_ratio_label = QLabel("Train Oranı (%):")
        self.train_ratio_input = QLineEdit()
        self.train_ratio_input.setPlaceholderText("Örneğin: 70")
        self.train_ratio_input.setFixedWidth(50)  # Genişliği 50px olarak ayarla
        self.train_ratio_input.setValidator(QIntValidator(0, 100))  # Sadece 0-100 arası tam sayılar
        
        self.val_ratio_label = QLabel("Validation Oranı (%):")
        self.val_ratio_input = QLineEdit()
        self.val_ratio_input.setPlaceholderText("Örneğin: 15")
        self.val_ratio_input.setFixedWidth(50)  # Genişliği 50px olarak ayarla
        self.val_ratio_input.setValidator(QIntValidator(0, 100))  # Sadece 0-100 arası tam sayılar
        
        self.test_ratio_label = QLabel("Test Oranı (%):")
        self.test_ratio_input = QLineEdit()
        self.test_ratio_input.setPlaceholderText("Örneğin: 15")
        self.test_ratio_input.setFixedWidth(50)  # Genişliği 50px olarak ayarla
        self.test_ratio_input.setValidator(QIntValidator(0, 100))  # Sadece 0-100 arası tam sayılar
        
        # Oranları yan yana yerleştirmek için yatay düzen
        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(self.train_ratio_label)
        ratio_layout.addWidget(self.train_ratio_input)
        ratio_layout.addWidget(self.val_ratio_label)
        ratio_layout.addWidget(self.val_ratio_input)
        ratio_layout.addWidget(self.test_ratio_label)
        ratio_layout.addWidget(self.test_ratio_input)
        
        layout.addLayout(ratio_layout)  # Oranları ekle

        # Alt bölge için container widget
        bottom_widget = QWidget()
        bottom_widget.setFixedHeight(60)
        bottom_layout = QHBoxLayout(bottom_widget)
        
        # Sol taraf için dikey düzen
        left_layout = QVBoxLayout()
        left_layout.setSpacing(0)
        
        # Output Type etiketi
        output_label = QLabel("Output Type")
        left_layout.addWidget(output_label)
        
        # Seçme kutusu
        self.output_combo = QComboBox()
        self.output_combo.setFixedWidth(90)
        
        # Öğeleri ekle
        self.output_combo.addItem("YOLOV11")
        
        # Devre dışı öğeleri ekle
        disabled_item1 = "YOLOV9"
        disabled_item2 = "YOLOV8"
        self.output_combo.addItem(disabled_item1)
        self.output_combo.addItem(disabled_item2)
        
        # İlgili öğeleri devre dışı bırak
        self.output_combo.model().item(1).setEnabled(False)  # YOLOV9
        self.output_combo.model().item(2).setEnabled(False)  # YOLOV8
        
        left_layout.addWidget(self.output_combo)
        
        # Sol taraf düzenini ana düzene ekle
        left_container = QWidget()
        left_container.setLayout(left_layout)
        bottom_layout.addWidget(left_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sağ taraftaki butonlar için dikey düzen
        button_layout = QVBoxLayout()
        button_layout.setSpacing(0)
        
        # Add butonu
        self.add_button = QPushButton('Add New Category')
        self.add_button.setFixedSize(100, 30)
        self.add_button.clicked.connect(self.show_add_dialog)
        button_layout.addWidget(self.add_button)
        
        # Create Dataset butonu
        self.create_dataset_button = QPushButton('Create Dataset')
        self.create_dataset_button.setFixedSize(100, 30)
        self.create_dataset_button.setEnabled(False)  # Başlangıçta devre dışı
        self.create_dataset_button.clicked.connect(self.create_dataset)
        button_layout.addWidget(self.create_dataset_button)
        
        # Butonları ana düzene ekle
        bottom_layout.addLayout(button_layout)
        
        # Alt bölgeyi ana düzene ekle
        layout.addWidget(bottom_widget)
        
    def init_decoder_tab(self):
        self.decoder_tab = QWidget()  # Decoder sekmesi için widget oluştur
        layout = QVBoxLayout(self.decoder_tab)  # Burada self.decoder_tab kullanmalısınız
        
        # Dataset listesi için ListView
        self.dataset_list = QListWidget()
        self.dataset_list.setMinimumHeight(300)  # Yükseklik 300px olarak ayarlandı
        self.dataset_list.setSelectionMode(QAbstractItemView.MultiSelection)  # Çoklu seçim modu
        
        # Modern stil
        self.dataset_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                height: 35px;
                padding-left: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        
        # Datasets klasöründeki klasörleri listele
        datasets_path = "datasets"
        if os.path.exists(datasets_path):
            for folder in os.listdir(datasets_path):
                folder_path = os.path.join(datasets_path, folder)
                if os.path.isdir(folder_path):
                    item = QListWidgetItem(folder)
                    self.dataset_list.addItem(item)
        
        # Seçim değişikliğini izle
        self.dataset_list.itemClicked.connect(self.on_dataset_selected)
        
        layout.addWidget(self.dataset_list)
        

        
        # Alt alan
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_widget.setFixedHeight(60)  # Yükseklik ayarı
        
        # Arka plan rengini gri yap
        bottom_widget.setStyleSheet("background-color: #f0f0f0;")  # Gri arka plan
        
        # Input Type etiketi
        input_type_label = QLabel("Input Type:")
        
        # ComboBox
        self.input_type_combo = QComboBox()
        self.input_type_combo.addItem("YOLOV11")  # Aktif
        self.input_type_combo.addItem("YOLOV10")  # Pasif
        self.input_type_combo.addItem("YOLOV9")   # Pasif
        
        # YOLOV10 ve YOLOV9'u pasif hale getir
        self.input_type_combo.model().item(1).setEnabled(False)  # YOLOV10
        self.input_type_combo.model().item(2).setEnabled(False)  # YOLOV9
        
        bottom_layout.addWidget(self.input_type_combo)
        
        # Decode butonu
        self.decode_button = QPushButton("Decode")
        self.decode_button.setFixedHeight(40)  # Yükseklik ayarı
        self.decode_button.clicked.connect(self.on_decode_clicked)  # Buton tıklama olayı
        bottom_layout.addWidget(self.decode_button)

        layout.addWidget(bottom_widget)
        layout.addStretch()  # Alt alanı en alta itmek için
    
    def on_dataset_selected(self, item):
        """Dataset seçildiğinde çağrılır"""
        selected_datasets = [self.dataset_list.item(i).text() for i in range(self.dataset_list.count()) if self.dataset_list.item(i).isSelected()]
        print(f"Seçilen datasetler: {selected_datasets}")
    
    def check_create_button(self):
        """Create Dataset butonunun durumunu kontrol et"""
        # Tabloda en az bir satır varsa butonu etkinleştir
        self.create_dataset_button.setEnabled(self.dataset_table.rowCount() > 0)
    
    def show_add_dialog(self):
        dialog = AddDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            category_name = dialog.name_input.text()
            selected_files = dialog.get_selected_files()
            if category_name and selected_files:
                # Yeni satır ekle
                row = self.dataset_table.rowCount()
                self.dataset_table.insertRow(row)
                
                # Kategori adını ve dosya sayısını ekle
                category_text = f"{category_name} ({len(selected_files)})"
                self.dataset_table.setItem(row, 0, QTableWidgetItem(category_text))
                
                # Seçilen dosyaları ekle
                files_text = ", ".join([os.path.basename(f) for f in selected_files])
                self.dataset_table.setItem(row, 1, QTableWidgetItem(files_text))
                
                # Toplamı hesapla ve yeni kolona ekle
                total_count = sum(int(num) for num in re.findall(r'\((\d+)\)', files_text))
                self.dataset_table.setItem(row, 2, QTableWidgetItem(str(total_count)))  # Toplam kolona ekle
                
                # Create Dataset butonunu kontrol et
                self.check_create_button()

    def show_edit_dialog(self, row, column):
        # Kategori ismini parantezden ayır
        full_category_text = self.dataset_table.item(row, 0).text()
        category_name = full_category_text.split(" (")[0]  # Parantezden önceki kısmı al
        files = self.dataset_table.item(row, 1).text().split(", ")
        
        dialog = EditDialog(category_name, files, self)
        if dialog.exec_() == QDialog.Accepted:
            new_category_name = dialog.name_input.text()
            selected_files = dialog.get_selected_files()
            
            if new_category_name and selected_files:
                # Tabloyu güncelle
                category_text = f"{new_category_name} ({len(selected_files)})"
                self.dataset_table.setItem(row, 0, QTableWidgetItem(category_text))
                files_text = ", ".join(selected_files)
                self.dataset_table.setItem(row, 1, QTableWidgetItem(files_text))

    def create_dataset(self):
        # Proje dizininde temp klasörünü oluştur
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)  # Klasör zaten varsa hata vermez
        os.makedirs(os.path.join(temp_dir, 'images'), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, 'labels'), exist_ok=True)

        # Tablodaki tüm kategorilerin seçili klasörlerini ve isimlerini topla
        selected_folders_list = []
        category_names = []
        row_count = self.dataset_table.rowCount()
        
        for row in range(row_count):
            # Dosyaları al
            files_text = self.dataset_table.item(row, 1).text()
            selected_folders = files_text.split(", ")
            selected_folders_list.append(selected_folders)
            
            # Kategori ismini al (parantezden önceki kısım)
            category_text = self.dataset_table.item(row, 0).text()
            category_name = category_text.split(" (")[0]
            category_names.append(category_name)
        
        # Kullanıcıdan oranları al
        try:
            train_ratio = float(self.train_ratio_input.text())
            val_ratio = float(self.val_ratio_input.text())
            test_ratio = float(self.test_ratio_input.text())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli sayılar girin.", QMessageBox.Ok)
            return

        # Oranların toplamını kontrol et
        if train_ratio + val_ratio + test_ratio != 100:
            QMessageBox.warning(self, "Hata", "Oranların toplamı 100 olmalıdır.", QMessageBox.Ok)
            return

        
        # Dataset oluştur
        if create_dataset(selected_folders_list, category_names, train_ratio / 100, val_ratio / 100, test_ratio / 100):
            QMessageBox.information(self, "Başarılı", 
                "Dataset oluşturuldu!\nKonum: output_dataset",
                QMessageBox.Ok)
        else:
            QMessageBox.critical(self, "Hata", 
                "Dataset oluşturulurken bir hata oluştu!",
                QMessageBox.Ok)
        
    def p(self,dataset_name):
        labels_path = os.path.join("datasets", dataset_name, "test", "labels")
            
        if os.path.exists(labels_path):
                # Tüm metin dosyalarını oku
            for label_file in os.listdir(labels_path):
                if label_file.endswith(".txt"):  # Sadece .txt dosyalarını oku
                    file_path = os.path.join(labels_path, label_file)
                    with open(file_path, 'r') as file:
                        content = file.read()
                        print(f"İçerik ({label_file}):\n{content}\n")  
    def on_decode_clicked(self):
        """Decode butonuna tıklandığında çağrılır"""
        selected_items = self.dataset_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir dataset seçin.")
            return
        
        for item in selected_items:
            dataset_name = item.text()
            self.p(dataset_name)
            yaml_path = os.path.join("datasets", dataset_name, "data.yaml")
            if self.decoder.load_yaml(yaml_path):
                self.reader.categorize_yolo11_datasets(item.text())
            else:
                QMessageBox.warning(self, "Hata", f"{dataset_name} için data.yaml yüklenemedi.")

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = Interface()
    window.show()
    sys.exit(app.exec_())


