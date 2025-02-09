import os
import yaml
from reader import reader
class Decoder:
    def __init__(self):
        self.class_names = []
        
    def load_yaml(self, yaml_path):
        """YAML dosyasından sınıf isimlerini yükle"""
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
                if 'names' in data:
                    self.class_names = data['names']
                    return True
                return False
        except Exception as e:
            print(f"YAML yükleme hatası: {str(e)}")
            return False
    
    def create_output_folders(self, output_path):
        """Output klasörlerini oluştur"""
        try:
            os.makedirs(output_path, exist_ok=True)
            for name in self.class_names:
                os.makedirs(os.path.join(output_path, name), exist_ok=True)
            print(f"Output klasörleri oluşturuldu: {output_path}")
            return True
        except Exception as e:
            print(f"Klasör oluşturma hatası: {str(e)}")
            return False 
    