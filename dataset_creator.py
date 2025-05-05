import os
import shutil
import random

class creator():
    def update_line_in_file_w(self, file_path, new_id):
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

    def create_dataset(self,selected_folders_list, category_names, train_ratio, val_ratio, test_ratio, max_images):
        """
        Seçili klasörlerdeki images ve labels dosyalarını YOLO v11 formatında output_dataset'e kopyalar
        
        Args:
            selected_folders_list: Her satırdaki seçili klasörlerin listesi
            category_names: Tablodaki kategori isimleri listesi
            train_ratio: Train oranı
            val_ratio: Validation oranı
            test_ratio: Test oranı
            max_images: Her kategoriden alınacak maksimum resim sayısı
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
                copied=0
                k=0
                
                for folder in folders:
                    if copied > max_images:
                        break
                    
                    source_folder = os.path.join("output", folder.split(" ")[0])
                    source_images = os.path.join(source_folder, "images")
                    source_labels = os.path.join(source_folder, "labels")

                    if not os.path.exists(source_images) or not os.path.exists(source_labels):
                        print(f"Kaynak klasörler bulunamadı: {source_folder}")
                        continue

                    total_files_in_folder = len(os.listdir(source_images))
                    k = k + total_files_in_folder
                    
                    if k <= max_images:
                        much_copy = total_files_in_folder
                    else:
                        much_copy = max_images - (k - total_files_in_folder)

                    for i, img in enumerate(os.listdir(source_images)):
                        if i >= much_copy:
                            break
                            
                        src_img_path = os.path.join(source_images, img)
                        src_lbl_path = os.path.join(source_labels, img.replace("jpg", "txt"))

                        if not os.path.isfile(src_img_path) or not os.path.isfile(src_lbl_path):
                            print(f"Dosya bulunamadı: {src_img_path} veya {src_lbl_path}")
                            continue

                        # Orana göre hedef klasörü belirle
                        if i < much_copy * train_ratio:
                            dst_path = os.path.join(output_dataset, 'train')
                        elif i < much_copy * (train_ratio + test_ratio):
                            dst_path = os.path.join(output_dataset, 'test')
                        else:
                            dst_path = os.path.join(output_dataset, 'valid')

                        # Rastgele dosya adı oluştur
                        first_digit = random.randint(1, 9)
                        remaining_digits = [random.randint(0, 9) for _ in range(30 - 1)]
                        random_number = str(first_digit) + ''.join(map(str, remaining_digits))

                        # Resmi kopyala ve yeniden adlandır
                        dst_img_path = os.path.join(dst_path, 'images', img)
                        shutil.copy2(src_img_path, dst_img_path)
                        
                        name = dst_img_path.split("\\")[:3]
                        name = "/".join(name)
                        new_name_path = f"{name}\\images_{random_number}.jpg" 
                        os.rename(dst_img_path, new_name_path)

                        # Etiketi kopyala, güncelle ve yeniden adlandır
                        dst_lbl_path = os.path.join(dst_path, 'labels', img.replace("jpg", "txt"))
                        label_path = shutil.copy2(src_lbl_path, dst_lbl_path)
                        self.update_line_in_file_w(label_path, str(index))

                        name = dst_lbl_path.split("\\")[:3]
                        name = "/".join(name)
                        new_name_path = f"{name}\\images_{random_number}.txt" 
                        os.rename(dst_lbl_path, new_name_path)
                        
                        copied += 1

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
