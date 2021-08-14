import os, glob
from pathlib import Path
from datetime import datetime 
from PIL import Image
from datetime import datetime
import requests
import uuid
import time
import base64
import json
import csv, re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from requests.models import encode_multipart_formdata
import urllib3
import pandas as pd
import pickle
from fuzzywuzzy import process, fuzz

# ssl에러 메시지 제거
urllib3.disable_warnings()

def initiate(paths_to_handle) :
    # 초기화 csv, jpg 파일을 지웁니다. alert도 보여주구요..

    def delete_files(files) :
        for f in files :
            os.remove(f)

    csv_to_delete = getListOfFiles(paths_to_handle[7])
    delete_files(csv_to_delete)
    jpg_to_delete = getListOfFiles(paths_to_handle[3])
    delete_files(jpg_to_delete)
    err_to_delete = getListOfFiles(paths_to_handle[5])
    delete_files(err_to_delete)


def select_type(json_data) :
    window = tk.Tk()

    def combo_click():
        global fine_venue
        fine_venue = venue.get()
        window.destroy()

    venue = tk.StringVar()
    window.title("부과기관")
    window.geometry("400x200+700+300") # 가로길이 X 세로길이 + 가로좌표 + 세로좌표 
    # window.config(font=("gulim", 15))

    Combobox1 = ttk.Combobox(textvariable=venue, width=30)
    Combobox1['value'] = ('지자체_광역', '지자체_시군구', '유료도로')
    Combobox1.current(0)

    Click_button = tk.Button(text="선택", command=combo_click)

    Combobox1.pack()
    Click_button.pack()

    window.mainloop()

# 기관별로 API Key 변경

    if fine_venue == "지자체_광역":
        api_url = json_data['secret']['metro_politan']['api_url']
        secret_key = json_data['secret']['metro_politan']['secret_key']

    elif fine_venue == "지자체_시군구":
        api_url = json_data['secret']['province']['api_url']
        secret_key = json_data['secret']['province']['secret_key']

    elif fine_venue == "유료도로":
        api_url = json_data['secret']['token_duty']['api_url']
        secret_key = json_data['secret']['token_duty']['secret_key']

    else :
        pass

    return fine_venue, api_url, secret_key


def split_tiffs(tiffs, dest_path) :
    
    for a, image in enumerate(tiffs) :
        im = Image.open(image)
        im_n = im.n_frames

        for i in range(im_n):
            try:
                im.seek(i)
                im.save(dest_path + working_date +'_%s%s.jpg'%(a,i,))
            except EOFError:
                break

def make_folder(json_data) :
    # 현재 작업폴더 가져오기
    current_dir = os.getcwd()
    
    def make_path(path_variable, path_name) :
        path_variable = os.path.join(current_dir, path_name) 
        if not os.path.isdir(path_variable):                                                           
            os.mkdir(path_variable)
        return path_variable

    paths_to_handle = []

    for k, v in json_data['folder'].items() :
        res_path = make_path(k, v)
        paths_to_handle.append(res_path)
    
    return paths_to_handle


def naver_ocr_processing(ocr_jpg_files, paths_to_handle, api_url, secret_key) :
    ocr_result = {}
    ocr_result_total = {}

    for b, ti in enumerate(ocr_jpg_files) :
        image_file = ti
        with open(image_file,'rb') as f:
            file_data = f.read()

        request_json = {
            'images': [
                {
                    'format': 'jpg',
                    'name': ocr_jpg_files[b],
                    'data': base64.b64encode(file_data).decode()
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        payload = json.dumps(request_json,).encode('UTF-8')
        headers = {
        'X-OCR-SECRET': secret_key,
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", api_url, headers=headers, data = payload, verify = False)
        rescode = response.status_code

        result = response.json()
        
        # response 결과에 따라 
        if (rescode == 200) :
            try :
                fields_num = len(result['images'][0]['fields'])
                
                uid = result['images'][0]['uid']
                title = result['images'][0]['title']['name']
                idx = b + 1

                i = 0
                ocr_result['title'] = title
                ocr_result['uid'] = uid

                for i in range(fields_num) :
                    field = result['images'][0]['fields'][i]['name']
                    infer_text = result['images'][0]['fields'][i]['inferText']
                    reg_expression = r"[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]"
                    infer_text = re.sub(reg_expression,"", infer_text)

                    try :
                        if field == '차량번호' :
                            id_pattern = r'\d{2,3}[가-힣]{1,2}\d{4}'  
                        
                            if id_pattern :
                                infer_text = "".join(re.findall(id_pattern, infer_text))                             
                            else :
                                infer_text = "" 
                                # omit_words = ['차량번호', '회사']
                                # if any(word in infer_text for word in omit_words):
                                #     infer_text = infer_text.replace(omit_words[0], '')
                                #     infer_text = infer_text.replace(omit_words[1], '')

                        elif field == '납부금액' :
                            infer_text = "".join(re.findall("\d+", infer_text))

                        elif field == '발급기관' :
                            infer_text = "".join(re.compile("[가-힣]+").findall(infer_text))
                                # "".join(re.findall("\[가-힣]+", infer_text))
                        
                        elif field == '위반일시' :
                            infer_text = "".join(re.findall("\d+", infer_text))
                            if len(infer_text) >=14 :
                                infer_text = infer_text[0:14]
                            else :
                                infer_text = infer_text.ljust(14, "0")

                        elif field == '납부기한' :
                            infer_text = "{0:0<8}".format("".join(re.findall("\d+", infer_text)))
                            if len(infer_text) >=9 :
                                infer_text = infer_text[0:8]
                            else :
                                infer_text = infer_text.ljust(8, "0")
                    except :
                        continue

                    ocr_result[field] = infer_text
                
                key_list = list(ocr_result.keys())

                if not '발급기관' in key_list  :
                    ocr_result['발급기관'] = ""

                ocr_result_total[uid] = ocr_result
                ocr_result_total[uid]['no'] = idx
                ocr_result = {} 
                car_reg_num = ocr_result_total[uid]['차량번호']
                office_issued = ocr_result_total[uid]['발급기관']
                violated_date = ocr_result_total[uid]['위반일시']
                
                # 차량번호가 있을경우와 없을 경우 예외처리

                if len(car_reg_num) < 1 :
                    
                    if len(office_issued) < 1 and len(violated_date) < 1 :
                        renamed_nm = title + "_(input차량번호)_(input위반일시)_" + Path(image_file).name
                        ocr_result_total[uid]['file_name'] = renamed_nm
                        dest_path = os.path.join(paths_to_handle[5], renamed_nm)
                        if os.path.exists(dest_path) :
                            os.rename(image_file, dest_path+'_{}'.format(b))
                        else :
                            os.rename(image_file, dest_path)

                    elif len(violated_date) < 1 and len(office_issued) >= 1 :
                        renamed_nm = title + "_" + office_issued+ "_(input차량번호)_(input위반일시).jpg"
                        ocr_result_total[uid]['file_name'] = renamed_nm
                        dest_path = os.path.join(paths_to_handle[5], renamed_nm)
                        if os.path.exists(dest_path) :
                            os.rename(image_file, dest_path+'_{}'.format(b))
                        else :
                            os.rename(image_file, dest_path)

                    elif len(violated_date) >= 1 and len(office_issued) < 1 :
                        renamed_nm = title + "_(input차량번호)_" + violated_date+ ".jpg"
                        ocr_result_total[uid]['file_name'] = renamed_nm
                        dest_path = os.path.join(paths_to_handle[5], renamed_nm)
                        if os.path.exists(dest_path) :
                            os.rename(image_file, dest_path+'_{}'.format(b))
                        else :
                            os.rename(image_file, dest_path)
                    
                    else :
                        renamed_nm = title + "_" + office_issued+"_(input차량번호)_"+ violated_date+ ".jpg"
                        ocr_result_total[uid]['file_name'] = renamed_nm
                        dest_path = os.path.join(paths_to_handle[5], renamed_nm)
                        if os.path.exists(dest_path) :
                            os.rename(image_file, dest_path+'_{}'.format(b))
                        else :
                            os.rename(image_file, dest_path)
                
                else :
                    if len(office_issued) < 1 and len(violated_date) < 1 :
                        renamed_nm = title + car_reg_num+ "_(input위반일시).jpg"
                        path_compare = os.path.join(paths_to_handle[3], renamed_nm) 
                        if os.path.exists(path_compare):                                                           
                            renamed_nm = title + car_reg_num+ "_(input위반일시).jpg"
                            os.rename(image_file, os.path.join(paths_to_handle[3], renamed_nm))
                        else :
                            os.rename(image_file, os.path.join(paths_to_handle[3], renamed_nm))
                            ocr_result_total[uid]['file_name'] = renamed_nm

                    elif len(violated_date) < 1 and len(office_issued) >= 1:
                        renamed_nm = title + "_" + office_issued+ "_" + car_reg_num+ "_(input위반일시).jpg"
                        ocr_result_total[uid]['file_name'] = renamed_nm
                        dest_path = os.path.join(paths_to_handle[3], renamed_nm)
                        if os.path.exists(dest_path) :
                            os.rename(image_file, dest_path+'_{}'.format(b))
                        else :
                            os.rename(image_file, dest_path)

                    elif len(violated_date) >= 1 and len(office_issued) < 1 :
                        renamed_nm = title + "_" +  car_reg_num+ "_" + violated_date+ ".jpg"
                        ocr_result_total[uid]['file_name'] = renamed_nm
                        dest_path = os.path.join(paths_to_handle[3], renamed_nm)
                        if os.path.exists(dest_path) :
                            os.rename(image_file, dest_path+'_{}'.format(b))
                        else :
                            os.rename(image_file, dest_path)
                    
                    else :
                        renamed_nm = title + "_" + office_issued + "_" + car_reg_num + "_" + violated_date + ".jpg"
                        ocr_result_total[uid]['file_name'] = renamed_nm
                        dest_path = os.path.join(paths_to_handle[3], renamed_nm)
                        if os.path.exists(dest_path) :
                            os.rename(image_file, dest_path+'_{}'.format(b))
                        else :
                            os.rename(image_file, dest_path)

                print(renamed_nm + " is processed.")
                time.sleep(0.2)
            
            except :
                os.rename(image_file, os.path.join(paths_to_handle[5], Path(image_file).name))

        else :
            print(response.text)           
            next
    
    daily_working_json_path = os.path.join(paths_to_handle[11], working_date[0:8]) 
    if not os.path.isdir(daily_working_json_path):                                                           
        os.mkdir(daily_working_json_path)
    json_file_name = 'ocr_results_json_{}.json'.format(working_date)

    with open(os.path.join(daily_working_json_path, json_file_name), 'w', encoding='utf-8') as f :
        json.dump(ocr_result_total, f, indent=4)
    
    xls_fields = ['no','file_name', 'title','발급기관', '행정기관', '차량번호', '위반장소', '위반일시', '위반내용', '납부기한', '납부금액']

    assorted_dict = {}
    for k, v in ocr_result_total.items() :
        assorted_dict[k] = {field : v.get(field) or "" for field in xls_fields}
    assorted_df = pd.DataFrame(data = assorted_dict).transpose()

    return assorted_df


def remove_specials(data) :
    data = re.sub('[-=·.#/?:$}]\s+', '', data)
    return "".join(re.compile("[가-힣]+").findall(data))

def ends_processing(data) :
    try : 
        if data.endswith('청') :
            data = data[:-1]
        elif data.endswith('청장') :
            data = data[:-2]
        elif data.endswith('장') :
            data = data[:-1]
        return data
    except :
        return ''

def end_word_processing(data) :
    try :
        busket = []
        data = data.strip()
        data_list = data.split(sep = " ")
        word_len = len(data_list)

        if data_list[-1].endswith('과') :
            sg_word = ['청장', '시장']
            if any(keyword in data_list[-1] for keyword in sg_word) :
                txt_temp = data_list[-1].split(sep = '장')
                for w in txt_temp :
                    txt = " ".join(ends_processing(w))

            txt = " ".join(data_list[i] for i in range(0, word_len-1))
            busket.append(txt)
        else :
            txt = " ".join(data_list[i] for i in range(0, word_len))
            busket.append(txt)
        return busket[0]
    except :
        return ''


def fine_gubun(data) :
    traffic_related = ['주정차', '주차금지', '교통', '횡단보도', '모퉁이', '보도', '속도위반', '교통소통','버스전용', '교차로', '주차구획', '소화전', '어린이보호구역', '주차방법', '거주자우선', '공영주차장', '부정주차']
    diabled_related = ['장애인전용']
    bus_only_related = ['버스전용']
    toll_related = ['유료도로', '미납통행료', '유료고속도로']
    if any(keyword in data for keyword in traffic_related) :
        return '도로교통 주정차위반'
    elif any(keyword in data for keyword in diabled_related) :
        return '장애인전용 주차위반'
    elif any(keyword in data for keyword in toll_related) :
        return '유료도로 미납통행료'
    elif any(keyword in data for keyword in bus_only_related) :
        return '버스전용차선 위반'
    else :
        return ''

def ocr_df_processing(df) :
    xls_raw_df = df.copy()
    office_cd = pd.read_csv(r'src\office_codes.csv', delimiter = '\t', dtype = {'관청코드' : str})
    office_split = pd.DataFrame(df['관청명(시군구)'].str.split(' ', 3).tolist(), columns=['L1','L2','L3', 'L4'])
    office_cd_df =  pd.concat([office_cd, office_split], axis = 1)

    xls_raw_df['office'] = xls_raw_df['title'] + xls_raw_df['발급기관'].fillna('') + xls_raw_df['행정기관'].fillna('')
    xls_raw_df['위반내용'] = xls_raw_df['위반내용'].apply(remove_specials)
    xls_raw_df['위반구분'] = xls_raw_df['위반내용'].apply(fine_gubun)

    df_office = office_cd_df[['관청구분', '관청명(시군구)', '관청코드', '관할업무', 'L1','L2','L3', 'L4']].reset_index()
    df_office = df_office[~office_cd_refined_df['관청명(시군구)'].isnull()]

    merged_office_names = xls_raw_df['office'].to_list()
    merged_fine_reason = xls_raw_df['위반내용'].to_list()

    office_cd_extracted = []

    def find_match(name_list, name) :
        for keyword in name_list :
            if keyword in name : return keyword
            else : continue
        return None

    for i, name in enumerate(merged_office_names) :
        L1_office, L2_office, L3_office, L4_office, office_cd = None, None, None, None, None

        L1_list = df_office['L1'].unique()
        L1_office = find_match(L1_list, name)
        
        if L1_office is not None :
            L2_list_tmp = df_office['L2'][df_office['L1'] == L1_office].unique()
            L2_list = list(filter(None, L2_list_tmp))
            L2_office = find_match(L2_list, name)

            if L2_office is not None :
                L3_list_tmp = df_office['L3'][(df_office['L1'] == L1_office) & (df_office['L2'] == L2_office)].unique()
                L3_list = list(filter(None, L3_list_tmp))
                L3_office = find_match(L3_list, name)

                if L3_office is not None :
                    L4_list_tmp = df_office['L4'][(df_office['L1'] == L1_office) & (df_office['L2'] == L2_office) &  (df_office['L3'] == L3_office)].unique()
                    L4_list = list(filter(None, L4_list_tmp))
                    L4_office = find_match(L4_list, name)

                    if L4_office is None :
                        office_cd_list = df_office['관청코드'][(df_office['L1'] == L1_office) & (df_office['L2'] == L2_office)& (df_office['L3'] == L3_office)].to_list()
                        # if len(office_cd_list) == 1 : office_cd = office_cd_list[0]
                        office_cd = office_cd_list[0]
                        # else : office_cd = None

                    else :
                        office_cd_list = df_office['관청코드'][(df_office['L1'] == L1_office) & (df_office['L2'] == L2_office) & (df_office['L3'] == L3_office)& (df_office['L4'] == L4_office)].to_list()
                        if len(office_cd_list) == 1 : office_cd = office_cd_list[0] 
                        else : office_cd = None

                else : 
                    L3_office = None
                    office_cd_list = df_office['관청코드'][(df_office['L1'] == L1_office) & (df_office['L2'] == L2_office)].to_list()
                    if len(office_cd_list) == 1 : office_cd = office_cd_list[0]
                    elif len(office_cd_list) > 1 :
                        office_cd_list = df_office['관청코드'][(df_office['L1'] == L1_office) & (df_office['L2'] == L2_office) & (df_office['관할업무'] == merged_fine_reason[i])].to_list()
                        print(merged_fine_reason[i])
                        if len(office_cd_list) == 1 : office_cd = office_cd_list[0]
                    else : office_cd = None

            else : 
                L2_office = None
                office_cd_list = df_office['관청코드'][df_office['L1'] == L1_office].to_list()
                if len(office_cd_list) == 1 : office_cd = office_cd_list[0]
                else : office_cd = None

        else : L1_office = None

        office_cd_extracted.append(office_cd)
    
    xls_raw_df['관청코드_upload'] = office_cd_extracted
    
    def find_office_name(df_office, cd) :
        try :
            office_name = df_office['관청명(시군구)'][df_office['관청코드'] == cd].to_list()[0]
            return office_name
        except :
            return None
        
    xls_raw_df['관청명칭_upload'] = total_df['관청코드_upload'].apply(lambda x : find_office_name(df_office, x))
    
    return xls_raw_df


def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
            
        else:
            allFiles.append(fullPath)
                
    return allFiles

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def main():
    
    global working_date
    working_date = datetime.today().strftime('%Y%m%d%H%M')
    
    with open(r'src\constants.json') as json_file:
        json_data = json.load(json_file)
    paths_to_handle = make_folder(json_data)    
    
    # init_yn = messagebox.askyesnocancel(title="Initiation", message="기존 OCR 결과 csv 파일과 jpg 파일을 지우고 Naver OCR을 구동합니다. 지우고 시작하려면 Yes를, 지우지 않고 시작하려면 No를, 중지하고 싶으면 Cancel을 눌러주세요.")
    # if init_yn :
    #     initiate(paths_to_handle)
    # elif init_yn is False:
    #     pass
    # else :
    #     os._exit(1)
    # images_to_ocr_path, images_to_non_ocr_path, images_processing_path, ocr_to_jpg_path, non_ocr_to_jpg_path, ocr_error_path, jpg_to_mac_upload_path, ocr_result_csv_path = make_folder()
    
    fine_venue, api_url, secret_key = select_type(json_data)

    # ocr 대상 tiffs 파일 읽어서 jpg로 쪼개고 tiff 파일 지우기
    tiffs_files = getListOfFiles(paths_to_handle[0])
    split_tiffs(tiffs_files, paths_to_handle[2])
    print("Tiffs to jpgs splitted complete!")
    
    ocr_jpg_files = glob.glob(paths_to_handle[2]+'*.jpg')
    ocr_return_df = naver_ocr_processing(ocr_jpg_files, paths_to_handle, api_url, secret_key)
    processed_df = ocr_df_processing(ocr_return_df)
    xlsx_file_name = "naver_ocr_result_" + working_date + '.xlsx'
    xls_fields = ['no','file_name', 'title','발급기관', '차량번호', '위반장소', '위반일시', '위반내용', '납부기한', '납부금액', '관청코드_upload', '관청명칭_upload']
    processed_df = processed_df[xls_fields]
    processed_df.to_excel(os.path.join(paths_to_handle[7], xlsx_file_name), index=False)

    print('OCR Result saved in excel.!!')
    
    files_to_remove = glob.glob(paths_to_handle[2]+'*.*')
    for file in files_to_remove :
        os.remove(file)
    os.rmdir(paths_to_handle[2])
    print("Remove temporary folder completed!")

    daily_working_path = os.path.join(paths_to_handle[8], working_date[0:8]) 
    if not os.path.isdir(daily_working_path):                                                           
        os.mkdir(daily_working_path)

    if fine_venue == '지자체_광역' :       
        for i, files in enumerate(tiffs_files) :
            renamed_raw = 'metro_politan_{}_{}'.format(working_date, i)
            os.rename(files, os.path.join(daily_working_path, renamed_raw))
    elif fine_venue == '지자체_시군구' :       
        for i, files in enumerate(tiffs_files) :
            renamed_raw = 'rural_province_{}_{}'.format(working_date, i)
            os.rename(files, os.path.join(daily_working_path, renamed_raw))
    else : 
        for i, files in enumerate(tiffs_files) :
            renamed_raw = 'toll_duty_{}_{}'.format(working_date, i)
            os.rename(files, os.path.join(daily_working_path, renamed_raw))
    
    print("Move Tiffs to Data Folder completed!")
    
    print("All Done")

if __name__ == '__main__':
    main()
