import os
import shutil
import yaml


def read_yaml(dataset_path):
    try:
        with open(f"{dataset_path}\\data.yaml", "r") as file:
            data = yaml.safe_load(file)
        print(data["names"])
        relative_paths= [data["names"],data["train"],data["test"]]
        return relative_paths
    except FileNotFoundError:
        print("The file was not found.")
    except yaml.YAMLError as exc:
        print("Error while parsing YAML:", exc)
    
   

   
   

def read_yolo11_datasets(dataset_path,output_path):
    

    # Çıkış klasörlerini oluştur
    os.makedirs(output_path, exist_ok=True)
    images_output = os.path.join(output_path, "images")
    labels_output = os.path.join(output_path, "labels")
    os.makedirs(images_output, exist_ok=True)
    os.makedirs(labels_output, exist_ok=True)

 
    image_count = 0
    class_item_count=[]
  
    images_path = os.path.join(dataset_path, "images")
    labels_path = os.path.join(dataset_path, "labels")

    for label_file in os.listdir(labels_path):
        label_path = os.path.join(labels_path, label_file)
        image_file = label_file.replace(".txt", ".jpg")
        image_path = os.path.join(images_path, image_file)

        if not os.path.exists(image_path):
            continue  # Etiketin görüntüsü yoksa atla

        # Hedef sınıfı içeren etiketleri kontrol et
        
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
   

def read_yolo11_datasets(dataset_path,output_path):
    

    # Çıkış klasörlerini oluştur
    os.makedirs(output_path, exist_ok=True)
    images_output = os.path.join(output_path, "images")
    labels_output = os.path.join(output_path, "labels")
    os.makedirs(images_output, exist_ok=True)
    os.makedirs(labels_output, exist_ok=True)

 
    image_count = 0

  
    images_path = os.path.join(dataset_path, "images")
    labels_path = os.path.join(dataset_path, "labels")

    for label_file in os.listdir(labels_path):
        label_path = os.path.join(labels_path, label_file)
        image_file = label_file.replace(".txt", ".jpg")
        image_path = os.path.join(images_path, image_file)

        if not os.path.exists(image_path):
            continue  # Etiketin görüntüsü yoksa atla

        # Hedef sınıfı içeren etiketleri kontrol et
        with open(label_path, "r") as f:
            lines = f.readlines()

            filtered_lines = [line for line in lines if line.startswith(f"{dataset} ")]

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


def merge_yolo_datasets(dataset1_path, dataset2_path, output_path, target_class_id):
    # Çıkış klasörlerini oluştur
    os.makedirs(output_path, exist_ok=True)
    images_output = os.path.join(output_path, "images")
    labels_output = os.path.join(output_path, "labels")
    os.makedirs(images_output, exist_ok=True)
    os.makedirs(labels_output, exist_ok=True)

    # Görüntü ve etiket dosyalarını birleştir
    dataset_paths = [dataset1_path, dataset2_path]
    image_count = 0

    for dataset_path in dataset_paths:
        images_path = os.path.join(dataset_path, "images")
        labels_path = os.path.join(dataset_path, "labels")

        for label_file in os.listdir(labels_path):
            label_path = os.path.join(labels_path, label_file)
            image_file = label_file.replace(".txt", ".jpg")
            image_path = os.path.join(images_path, image_file)

            if not os.path.exists(image_path):
                continue  # Etiketin görüntüsü yoksa atla

            # Hedef sınıfı içeren etiketleri kontrol et
            with open(label_path, "r") as f:
                lines = f.readlines()

            filtered_lines = [line for line in lines if line.startswith(f"{target_class_id} ")]

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
# Kullanım
dataset = "datasets\\simulasyon-1"  # İlk veri setinin yolu
#dataset2 = "datasets/sol-2/train"  # İkinci veri setinin yolu
output = "output"      # Çıkış klasörünün yolu
#target_class_id = "0"          # İstediğiniz sınıfın id'si (ör. '0', '1')

#merge_yolo_datasets(dataset1, dataset2, output, target_class_id)
read_yaml(dataset)
read_yolo11_datasets(f"{dataset}//train",output)