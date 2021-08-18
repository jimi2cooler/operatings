import re, glob
import pandas as pd
import os
from pdf2image import convert_from_path
from pathlib import Path

path_pdfs = r'rsc/lease_contract_pdfs/'
path_csv = r'rsc/lease_contract_csv/'
dest_path = r'output/lease_contract_jpg/'

# 초기화 : 기존 파일 제거
files_to_remove = glob.glob(dest_path+'*.*')
for file in files_to_remove :
    os.remove(file)
print("Remove previous images completed!")

pdf_files = glob.glob(path_pdfs+'*.pdf')[0]
csv_files = glob.glob(path_csv+'*.csv')[0]

# extract file_names 
file_name_df = pd.read_csv(csv_files, delimiter = '\t')
file_name_df['file_name'] = file_name_df['관청명(시군구)'] + '_' + file_name_df['차량번호'] + '_' + file_name_df['위반일시'].apply(lambda x : "".join(re.findall("\d+", x))) + '_contract'
mapping_list = file_name_df['file_name'].to_list()

# pdf 파일 읽어서 메모리의 이미지를 output_folder에 시스템 파일명으로 저장
images = convert_from_path(pdf_files, output_folder=dest_path, fmt="jpg", dpi = 300) #dpi=200, grayscale=True, size=(300,400), first_page=0, last_page=3)        
images.clear()
print('Completed convert pdf files to jpg files.!')

# output_folder에 저장된 이미지 파일 List 읽기
img_files = glob.glob(dest_path + '*.*')

if len(mapping_list) == len(img_files) :
    for img in img_files:
        img_name_stem = Path(img).stem
        order_list = img_name_stem.split(sep = '-')
        order_num = int(order_list[-1]) 
        save_file_name = mapping_list[order_num-1] +'.jpg'
        save_path = os.path.join(dest_path, save_file_name)
        os.rename(img, save_path)
else :
    "File number error!"

print("Renamed images, Done! \n All Done ! ")

