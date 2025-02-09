from reader import reader
rd = reader()

#catagories_names = rd.read_yaml(dataset_names[0])[0]

rd.categorize_yolo11_datasets("sol-2","output")