import os
import shutil
import yaml
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np



class reader():
    def __init__(self):
        self.current_image = None
        self.current_pixmap = None
        
    def read_yaml(self,dataset_name,c):
        try:
            with open(f"datasets\\{dataset_name}\\data.yaml", "r") as file:
                data = yaml.safe_load(file)
            relative_paths= [data["names"],data["train"],data["test"],data["roboflow"]["project"]]

            if c:
                print("Proje adı:" + data["roboflow"]["project"])
                print("Katagori isimleri:")
                i=1
                for cat in data["names"]:
                    print("  "+str(i)+"- " + cat)
                    i=i+1
 
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
        catagories= self.read_yaml(dataset_name,False)[0]
        count_list =  [0] * len(catagories)
        folders=["test","train","valid"]
        for folder in folders:
            for label_file in os.listdir(f"datasets\\{dataset_name}\\{folder}\\labels"):
                with open(f"datasets\\{dataset_name}\\{folder}\\labels\\{label_file}", "r") as file:
                    for line in file:
                        first_word = line.split()[0] if line.strip() else None
                        if first_word:
                            count_list[int(first_word)]=count_list[int(first_word)]+1
        
        
        return count_list
    
 

    def categorize_yolo11_datasets(self, dataset_name,):
        catagories= self.read_yaml(dataset_name,False)[0]
        count_list =  [0] * len(catagories)
        # Create output directories
        os.makedirs("output", exist_ok=True)
        
        categories = self.read_yaml(dataset_name, False)[0]

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
        

    """
    def catagorize_yolo11_datasets(self,dataset_name,output_path):
        # Çıkış klasörlerini oluştur
        print("a")
        os.makedirs(output_path, exist_ok=True)
        catagories= self.read_yaml(dataset_name,False)[0]

        for cat_ in catagories:
            os.makedirs(os.path.join(output_path,cat_),exist_ok=True)
            os.makedirs(os.path.join(f"{output_path}/{cat_}","images"),exist_ok=True)
            os.makedirs(os.path.join(f"{output_path}/{cat_}","labels"),exist_ok=True)
            
        
       

    
        image_count=0
        
        images_path = os.path.join(dataset_name, "images")
        labels_path = os.path.join(dataset_name, "labels")
        print(images_path)

        folders=["test","train","valid"]
        for folder in folders:
            images_path = os.path.join("datasets", f"{dataset_name}\{folder}\images")
            labels_path = os.path.join("datasets", f"{dataset_name}\{folder}\labels")
            for label_file in os.listdir(f"datasets\{dataset_name}\{folder}\labels"):
                label_path = os.path.join(labels_path, label_file)
                image_file = label_file.replace(".txt", ".jpg")
                image_path = os.path.join(images_path, image_file)
                

                with open(f"datasets\\{dataset_name}\\{folder}\\labels\\{label_file}", "r") as file:
                            
                    
                    for line in file:
                        print(line)

                        first_word = line.split()[0] if line.strip() else None
                        if first_word:
                            print("ab")
                            new_image_file = f"image_{image_count}.jpg"
                            new_label_file = f"image_{image_count}.txt"
                            print(image_count)
                            # Görüntü ve etiket dosyalarını kopyala
                            shutil.copy(image_path, os.path.join(f"output\{catagories[int(first_word)]}\images", new_image_file))

                            shutil.copy(label_path, os.path.join(f"output\{catagories[int(first_word)]}\labels", new_label_file))
                            
                            with open(os.path.join(f"output\{catagories(int(first_word))}\labels", new_label_file), "w") as f:
                                f.writelines(filtered_lines)
                           
                           

                            # Görüntü ve etiket dosyalarını kopyala 
                           
                           
                            image_count += 1
                            print(catagories[int(first_word)])
        print(images_path)
        print(labels_path)


        
       
        for label_file in os.listdir(labels_path):
            label_path = os.path.join(labels_path, label_file)
            image_file = label_file.replace(".txt", ".jpg")
            image_path = os.path.join(images_path, image_file)

            if not os.path.exists(image_path):
                continue  # Etiketin görüntüsü yoksa atla

            
            with open(label_path, "r") as f:
                
                image_count = 0

                lines = f.readlines()

                filtered_lines = [line for line in lines if line.startswith("0")]

                print(filtered_lines)

                if filtered_lines:
                    # Yeni görüntü ve etiket dosyalarının yollarını belirle
                    new_image_file = f"image_{image_count}.jpg"
                    new_label_file = f"image_{image_count}.txt"

                    # Görüntü ve etiket dosyalarını kopyala
                    shutil.copy(image_path, os.path.join(images_output, new_image_file))

                    with open(os.path.join(labels_output, new_label_file), "w") as f:
                        f.writelines(filtered_lines)

                    image_count += 1

        print(f"Birleştirme tamamlandı. {image_count} resim kaydedildi.")

    
"""

  
