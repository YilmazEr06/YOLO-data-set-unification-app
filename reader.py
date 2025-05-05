import os
import shutil
import yaml
from PyQt5.QtGui import QImage, QPixmap

import numpy as np



class reader():
    def __init__(self):
        self.current_image = None
        self.current_pixmap = None

    def read_yaml(self,dataset_name):
        try:
            with open(f"datasets\\{dataset_name}\\data.yaml", "r") as file:
                data = yaml.safe_load(file)
            relative_paths= [data["names"],data["train"],data["test"]]
            
 
            return relative_paths
        except FileNotFoundError:
            print("Dosya bulunamadı.")
        except yaml.YAMLError as exc:
            print("Error while parsing YAML:", exc)

    def read_yaml1(self,dataset_name):
        try:
            with open(f"{dataset_name}\\data.yaml", "r") as file:
                data = yaml.safe_load(file)
            relative_paths= [data["names"],data["train"],data["test"]]
            
 
            return relative_paths
        except FileNotFoundError:
            print("Dosya bulunamadı.")
        except yaml.YAMLError as exc:
            print("Error while parsing YAML:", exc)

    def read_dataset_folder(self,c):
        # Klasörün yolu
        folder_path = "datasets"
        # Dosya isimlerini listeleme
        file_names = os.listdir(folder_path)
        if c:
            print("Dizindeki verisetleri:")
            i=1
            for file in file_names:
                print(str(i)+"- "+ file)
                i=i+1
        
        return file_names
    
    def count_yolo11_datasets(self,dataset_name):
        catagories= self.read_yaml1(dataset_name)[0]
        count_list =  [0] * len(catagories)
        folders=["test","train","valid"]
        for folder in folders:
            for label_file in os.listdir(f"{dataset_name}\\{folder}\\labels"):
                with open(f"{dataset_name}\\{folder}\\labels\\{label_file}", "r") as file:
                    for line in file:
                        first_word = line.split()[0] if line.strip() else None
                        if first_word:
                            count_list[int(first_word)]=count_list[int(first_word)]+1
        
        
        return count_list
    
 

    def categorize_yolo11_datasets(self, dataset_name):
        catagories = self.read_yaml(dataset_name)[0]
        count_list =  [0] * len(catagories)
        # Create output directories
        os.makedirs("output", exist_ok=True)
        
        categories = self.read_yaml(dataset_name)[0]

        for category in categories:
            category_path = os.path.join("output", category)
            os.makedirs(os.path.join(category_path, "images"), exist_ok=True)
            os.makedirs(os.path.join(category_path, "labels"), exist_ok=True)

        image_count = 0
        folders = ["test", "train", "valid"]

        for folder in folders:
            images_path = os.path.join("datasets", dataset_name, folder, "images")
            labels_path = os.path.join("datasets", dataset_name, folder, "labels")

            if not os.path.exists(labels_path):
                print(f"Warning: Label path does not exist: {labels_path}")
                continue

            for label_file in os.listdir(labels_path):
                label_path = os.path.join(labels_path, label_file)
                image_file = label_file.replace(".txt", ".jpg")
                image_path = os.path.join(images_path, image_file)

                if not os.path.exists(image_path):
                    print(f"Warning: Image file does not exist: {image_path}")
                    continue

                with open(label_path, "r") as lines:
                    for index,line in enumerate(lines):
                        line = line.strip()
                        if not line:
                            continue
                        
                        first_word = line.split()[0]
                        try:
                            category_index = int(first_word)
                            category_name = categories[category_index]
                            new_line = f"w {line[len(first_word) + 1:]}" 
                        except (ValueError, IndexError):
                            print(f"Error: Invalid category index {first_word} in file {label_path}")
                            continue

                        new_image_file = f"image_{image_count}.jpg"
                        new_label_file = f"image_{image_count}.txt"
                        
                        # Copy files to the appropriate category folder
                        shutil.copy(image_path, os.path.join("output", category_name, "images", new_image_file))
                        copied_file_path =  shutil.copy(label_path, os.path.join("output", category_name, "labels", new_label_file))
                        self.update_line_in_file(copied_file_path,index,new_line)

                        count_list[int(first_word)]=count_list[int(first_word)]+1
                        image_count += 1
        
        for i in range(len(catagories)):
            print(f"{catagories[i]}: {count_list[i]}"  )
        print("Categorization completed successfully.")
        return count_list

    def update_line_in_file(self,file_path, line_number, new_content):
        try:
            # Dosyayı oku
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Belirli bir satırı güncelle
            if 0 <= line_number < len(lines):
                lines[line_number] = new_content + '\n'  # Yeni içeriği ekle

            # Güncellenmiş içeriği dosyaya yaz
            with open(file_path, 'w') as file:
                file.writelines(lines)

           
        except FileNotFoundError:
            print("Dosya bulunamadı.")
        except Exception as e:
            print(f"Hata: {str(e)}")
        


  
