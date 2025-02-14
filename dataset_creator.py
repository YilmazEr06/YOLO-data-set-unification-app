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
        
        os.makedirs(output_dataset, exist_ok=True)
        
        # Train, val, test klasörlerini ve alt klasörlerini oluştur
        for split in ['train', 'valid', 'test']:
            split_path = os.path.join(output_dataset, split)
            os.makedirs(os.path.join(split_path, 'images'), exist_ok=True)
            os.makedirs(os.path.join(split_path, 'labels'), exist_ok=True)
        
       
        # Tüm seçili klasörleri işle
        for index, folders in enumerate(selected_folders_list):
            print(folders)
            for folder in folders:
                source_folder = os.path.join("output", folder.split(" ")[0])
                source_images = os.path.join(source_folder, "images")
               

                source_labels = os.path.join(source_folder, "labels")
                total_files_in_folder = len(os.listdir(source_images))
                print(source_images)

                
                for i ,img in enumerate(os.listdir(source_images)):
                        
                        
                        
                        if i<=total_files_in_folder*train_ratio:
                            dst_path = "output_dataset/train"
                        elif i<= total_files_in_folder*(train_ratio+test_ratio):
                            dst_path = "output_dataset/test"
                        else :
                            dst_path = "output_dataset/valid"

                        src_img_path = os.path.join(source_images, img)
                        dst_img_path = os.path.join(dst_path , 'images', img)

                       

                        if os.path.isfile(src_img_path):
                            try:
                                shutil.copy2(src_img_path, dst_img_path)
                            except Exception as e:
                                print(f"Resim kopyalanamadı: {str(e)}")

                            
                        
                        src_lbl_path = os.path.join(source_labels, img.replace("jpg","txt"))
                        dst_lbl_path = os.path.join(dst_path , 'labels', img.replace("jpg","txt"))
                        
                        try:    
                                label_path = shutil.copy2(src_lbl_path, dst_lbl_path)
                                update_line_in_file_w(label_path, str(index), len(category_names))
                        except Exception as e:
                                print(f"Etiket kopyalanamadı: {str(e)}")
                        
                """
                # Images klasörünü train klasörüne kopyala
                source_images = os.path.join(source_folder, "images")
                print(os.path.exists(source_images))
                if os.path.exists(source_images):
                    for img in os.listdir(source_images):
                        src_path = os.path.join(source_images, img)
                        dst_path = os.path.join(temp , 'images', img)
                        if os.path.isfile(src_path):
                            try:
                                shutil.copy2(src_path, dst_path)
                            except Exception as e:
                                print(f"Resim kopyalanamadı: {str(e)}")


                
                # Labels klasörünü train klasörüne kopyala
                source_labels = os.path.join(source_folder, "labels")
                if os.path.exists(source_labels):
                    for lbl in os.listdir(source_labels):
                        src_path = os.path.join(source_labels, lbl)
                        dst_path = os.path.join(temp,  'labels', lbl)
                        if os.path.isfile(src_path):
                            try:
                                label_path = shutil.copy2(src_path, dst_path)
                                update_line_in_file_w(label_path, str(index), len(category_names))
                            except Exception as e:
                                print(f"Etiket kopyalanamadı: {str(e)}")
        
                   

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
        

        
        """
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
        print(total_files_in_folder,train_ratio,test_ratio)
        return True
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return False 