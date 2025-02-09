import os
import shutil
import yaml
import random

def update_line_in_file_w(file_path, new_id,maxid):
        try:
            # Dosyayı oku
            with open(file_path, 'r') as file:
                lines = file.readlines()
                for index,line in enumerate(lines):
                    first_word = line.split()[0]
                    if first_word == "w":
                        new_line =  f"{new_id} {line[len(first_word) + 1:]}" 
                        # Belirli bir satırı güncelle
                        if 0 <= index < len(lines):
                            lines[index] = new_line   # Yeni içeriği ekle
                        # Güncellenmiş içeriği dosyaya yaz
                    else:
                        new_line=""
                        if 0 <= index < len(lines):
                            lines[index] = new_line 
            with open(file_path, 'w') as file:
                file.writelines(lines)

           
        except FileNotFoundError:
            print("Dosya bulunamadı.")
        except Exception as e:
            print(f"Hata: {str(e)}")
def create_dataset(selected_folders_list, category_names, train_ratio, val_ratio, test_ratio):
    """
    Seçili klasörlerdeki images ve labels dosyalarını YOLO v11 formatında output_dataset'e kopyalar
    
    Args:
        selected_folders_list: Her satırdaki seçili klasörlerin listesi
        category_names: Tablodaki kategori isimleri listesi
        train_ratio: Train oranı
        val_ratio: Validation oranı
        test_ratio: Test oranı
    """
    try:
        # Ana klasörü oluştur
        output_dataset = "output_dataset"
        temp = "temp"
        os.makedirs(output_dataset, exist_ok=True)
        
        # Train, val, test klasörlerini ve alt klasörlerini oluştur
        for split in ['train', 'val', 'test']:
            split_path = os.path.join(output_dataset, split)
            os.makedirs(os.path.join(split_path, 'images'), exist_ok=True)
            os.makedirs(os.path.join(split_path, 'labels'), exist_ok=True)
        
        # Tüm seçili klasörleri işle
        for index, folders in enumerate(selected_folders_list):
            for folder in folders:
                source_folder = os.path.join("output", folder)
                
                # Images klasörünü train klasörüne kopyala
                source_images = os.path.join(source_folder, "images")
                if os.path.exists(source_images):
                    for img in os.listdir(source_images):
                        src_path = os.path.join(source_images, img)
                        dst_path = os.path.join(temp , 'images', img)
                        if os.path.isfile(src_path):
                            shutil.copy2(src_path, dst_path)
                
                # Labels klasörünü train klasörüne kopyala
                source_labels = os.path.join(source_folder, "labels")
                if os.path.exists(source_labels):
                    for lbl in os.listdir(source_labels):
                        src_path = os.path.join(source_labels, lbl)
                        dst_path = os.path.join(temp,  'labels', lbl)
                        if os.path.isfile(src_path):
                            label_path = shutil.copy2(src_path, dst_path)
                            update_line_in_file_w(label_path, str(index), len(category_names))
        
        

        # Seçilen görselleri ve etiketlerini output dataset train klasörüne taşı
        folders = ["train","val","test"]
        ratios = [train_ratio,val_ratio,test_ratio]
        images =[]
        total_images = len(os.listdir(os.path.join(temp, 'images')))
        for index,folder in enumerate(folders):
            # Train oranına göre kaç görsel ve label taşınacağını hesapla
            
    
            num_images = int(total_images * ratios[index])

            # Rastgele görselleri seç
            all_images = os.listdir(os.path.join(temp, 'images'))
            selected_images = random.sample(all_images, num_images)
            for img in selected_images:
                img_src_path = os.path.join(temp, 'images', img)
                img_dst_path = os.path.join(output_dataset, folder, 'images', img)
                shutil.move(img_src_path, img_dst_path)

                # Aynı isme sahip label dosyasını taşı
                lbl_name = img.replace('.jpg', '.txt')  # Görsel uzantısına göre label uzantısını ayarla
                lbl_src_path = os.path.join(temp, 'labels', lbl_name)
                lbl_dst_path = os.path.join(output_dataset, folder, 'labels', lbl_name)
                shutil.move(lbl_src_path, lbl_dst_path)
        

        
        
        # YOLO v11 data.yaml dosyasını oluştur
        yaml_content = (
            f"train: ../train/images\n"
            f"val: ../valid/images\n"
            f"test: ../test/images\n"
            f"nc: {len(category_names)}\n"
            f"names: {str(category_names)}"
            
        )
        
        # data.yaml dosyasını kaydet
        yaml_path = os.path.join(output_dataset, "data.yaml")
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        return True
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return False 