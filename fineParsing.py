import os, glob
from pathlib import Path
from PIL import Image
from datetime import datetime, timedelta, date
import requests
import uuid
import time
import numpy as np
import json
import csv, re
from requests.models import encode_multipart_formdata
import urllib3
import pandas as pd
pd.options.mode.chained_assignment = None
import pickle
from fuzzywuzzy import process, fuzz

# ssl에러 메시지 제거
urllib3.disable_warnings()

def split_tiffs(tiffs, dest_path) :

    for a, image in enumerate(tiffs) :       
        im = Image.open(image)
        im_n = im.n_frames

        for i in range(im_n):
            try:
                im.seek(i)
                file_name = working_date + '_{}{}.jpg'.format(str(a).zfill(2),str(i+1).zfill(3))
                im.save(os.path.join(dest_path, file_name))
            except EOFError:
                break

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

# 담당과 찾기
def office_inCharge(x, div_cd):
    reg_x = r'(([가-힣]+)?(주차|관리|교통|장애|복지|차량|행복|가정|청소|가로|정비|사회|경제|안전|노인|위생|환경|도시|버스|민원)+([가-힣]+)?과)'
    
    office_cd = list(filter(lambda x : x.endswith('과'), div_cd))

    try:
        div_list = list(re.findall(reg_x, x))
        div_list = list(filter(lambda x : len(x) > 1, div_list))
        # for txt in div_list[0] :
        #     if txt in office_cd :
        #         print(txt)
        #         return txt
        intersect_list = list(set(div_list[0]).intersection(set(office_cd)))
        return intersect_list[0]
    except:
        return None

def change_officeName(x):
    filter_text = {'경남' : '경상남도', '경북' : '경상북도','전남':'전라남도','전북' : '전라북도','충남':'충청남도','충북':'충청북도','경기' : '경기도', '서울' : '서울특별시','제주':'제주도특별자치도', '세종특별시':'세종특별자치시',
                    '강원' : '강원도', '인천' : '인천광역시', '부산':'부산광역시', '대구':'대구광역시', '대전': '대전광역시', '광주':'광주광역시', '울산':'울산광역시'}
    new_list = []

    for txt in x.split(' ') :
        cnt = 0
        for k, v in filter_text.items() :
            if k == txt.strip() :
                new_list.append(v)
                cnt += 1
                break
        if cnt == 0 :
            new_list.append(txt.strip())

    return ' '.join(new_list)

# 개행단위로 Text 묶기
def full_context(df_parsed) :
    block_cnt = 1
    new_list = []
    block_words = ''
    x_left = []
    x_right = []
    y_upper = []
    y_lower = []
    for k, v in df_parsed.iterrows():

        if v['lineBreak'] == False:
            x_left.append(v['x'][0])
            x_right.append(v['x'][2])
            y_upper.append(v['y'][0])
            y_lower.append(v['y'][2])

            block_words = block_words + ' ' + v['inferText']

        else:
            x_left.append(v['x'][0])
            x_right.append(v['x'][2])
            y_upper.append(v['y'][0])
            y_lower.append(v['y'][2])

            block_words = block_words + ' ' + v['inferText']

            end_y = v['y'][2]
            temp = [block_words, min(x_left), max(
                x_right), min(y_upper), max(y_lower)]
            new_list.append(temp)
            block_cnt += 1
            block_words = ''
            x_left = []
            x_right = []
            y_upper = []
            y_lower = []
    return new_list

# 텍스트 형식의 데이터를 날짜형태로 변환
def make_date(x):
    num_text = ''.join(re.findall(r'\d+', x))
    yr = datetime.strftime(datetime.today(), '%Y')
    if (int(yr[0:2])-1 <= int(num_text[0:2]) <= int(yr[0:2])+1) or (int(yr[3:4])-1 <= int(num_text[0:2]) <= int(yr[3:4])+1) :
        if 13 <= len(num_text) <= 14:
            return pd.to_datetime(num_text, format='%Y%m%d%H%M%S', errors='coerce')
        elif 10 <= len(num_text) <= 12:
            if num_text.startswith('20') :
                return pd.to_datetime(num_text, format='%Y%m%d%H%M', errors='coerce')
            else :
                return pd.to_datetime(num_text, format='%y%m%d%H%M', errors='coerce')
        elif 6 <= len(num_text) <= 9:
            return pd.to_datetime(num_text, format='%Y%m%d', errors='coerce')
        elif len(num_text) < 6:
            return pd.to_datetime(num_text, format='%Y%m%d', errors='coerce')
        else:
            return pd.to_datetime(num_text, format='%c', errors='coerce')
    else :
        return None

# 위반일시 추출
def violation_time(x, toll_yn):

    if toll_yn == 'Y':

        # 혼잡통행료 예외 처리 (일자 데이터 사이 차량번호 제거)
        car_num_type = re.search(r'\d{2,3}\s?[ㄱ-ㅎ가-힣]{1}\s?\d{4}\s',  x)
        if car_num_type:
            x_adj = x.replace(car_num_type.group(), '')
        else:
            x_adj = x

        date_type = [r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}\s?\s?\d{1,2}\s?:\s?\d{2}\s?:\s?\d{2}', r'\d{4}년\s?\d{1,2}월\s?\d{1,2}일\s?\d{2}시\s?\d{2}분', r'\d{2,4}[-./]\d{1,2}[-./]\d{1,2}\s?\d{1,2}:?\d{1,2}',
                     r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}\s?[(/]?\d{1,2}\s?:?\s?\d{1,2}', r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}']

        for dt_type in date_type:
            try:
                date_text = re.search(dt_type, x_adj).group().replace(' ', '')
                return make_date(date_text)
            except:
                continue
        return None

    else:

        if any(a in x for a in ['위반 ', '위반일시', '주차일시', '주차', '위반 일시', '단속일시', '시간', '일시']):

            # 혼잡통행료 예외 처리 (일자 데이터 사이 차량번호 제거)
            car_num_type = re.search(r'\d{2,3}\s?[ㄱ-ㅎ가-힣]{1}\s?\d{4}\s', x)
            if car_num_type:
                x_adj = x.replace(car_num_type.group(), '')
            else:
                x_adj = x

            date_type = [r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}\s?\d{1,2}\s?:?\s?\d{2}\s?:?\s?\d{2}', r'\d{4}년\s?\d{1,2}월\s?\d{1,2}일\s?\d{2}시\s?\d{2}분', 
                         r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}[-./]?\s?[/(]?\d{1,2}\s?:?\s?\d{1,2}', r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}\s?(?\d{1,2}\s?:?\s?\d{1,2}']

            for dt_type in date_type:
                try:
                    date_text = re.search(dt_type, x_adj).group().replace(' ', '')
                    return make_date(date_text)
                except:
                    continue
        else:
            return None

# 납부기한 추출

def due_dates(x, toll_yn):
    
    filter_before = ['까지']
    for text in filter_before:
        if text in x:
            date_type = [r'\d{4}\s?[-./년]\s?\d{1,2}\s?[-./월]\s?\d{1,2}\s?[일]?']
            for dt_type in date_type:
                try:
                    start_index = re.search(text, x).start()
                    date_text = re.findall(dt_type, x[:start_index])
                    date_text = list(map(make_date, date_text))
                    return max(date_text)
                except:
                    next

    filter_after = ['기한 ', '납부기한', '납기내', '납기일', '납부일']

    for text in filter_after:
        if text in x:
            date_type = [r'\d{4}\s?[-./년]\s?\d{1,2}\s?[-./월]\s?\d{1,2}\s?[일]?']
            for dt_type in date_type:
                try:
                    start_index = re.search(text, x).start()
                    date_text = re.search(dt_type, x[start_index+len(text):], re.IGNORECASE).group().replace(' ', '')
                    return make_date(date_text)
                except:
                    next

    date_type = [r'\d{4}\s?[-./년]\s?\d{1,2}\s?[-./월]\s?\d{1,2}\s?[일]?']
    for dt_type in date_type:
        try:
            date_text = re.search(dt_type, x).group().replace(' ', '')
            return make_date(date_text)
        except:
            next
    return None


# 차량번호 추출

def get_carNum(x):
    except_num = ['01허1234', '99가1234', '77가1234']
    if any(a in x for a in ['과세대상 ', '차량번호', '부과대상']):

        data_type = [r'\d{2,3}\s?[가-힣]{1}\s?\d{4}']

        for data in data_type:
            try:
                carNum = re.search(data, x).group().replace(' ', '')
                if carNum in except_num :
                    return None
                else :
                    return carNum
            except:
                return None

    else:
        data_type = [r'\d{2,3}\s?[가-힣]{1}\s?\d{4}']

        for data in data_type:
            try:
                carNum = re.search(data, x).group().replace(' ', '')
                if carNum in except_num :
                    return None
                else :
                    return carNum
            except:
                return None

        return None

# 예외차량 번호 (예시 차량번호)
# '01허1234' , '99가1234'

# 전자납부번호 추출

def get_elecInvoice(x):
    for txt in re.split(r'\s|:', x):
        data_type = [r'\d{5}-\d{1}-\d{2}-\d{2}-\d{9}',
                     r'\d{5}-\d{1}-\d{2}-\d{2}-\d{1}-\d{7}-\d{1}', r'^ *\d[\d ]*$']  # 마지막은 숫자만 추출

        for i, word in enumerate(data_type):
            try:
                m = re.search(word, txt).group()
                if (i == 2) & (len(m) == 19):
                    return m.replace(' ', '')
                elif i < 2:
                    return m
            except:
                continue
    return None

# 납세번호 추출

def get_taxation(x):

    data_type = [r'\d[\d ]*$']  # 숫자만 추출

    for word in data_type:
        try:
            m = re.search(word, x).group()
            if (len(m) == 31) or (len(m) == 32) or (len(m) == 27): #부천도시공사는 27자리.. 확인필요
                return m.replace(' ', '')
        except:
            continue
    return None

# 납부금액 추출

def get_amount(x):
    filter_text = ['합계금액', '총합계', '합 계', '감경금액', '납기내 금액', '납부금액 (20%감경금액)', '기한내', '기한 내', '미납요금','납부액', '납부금액', '금액', '금 액', '부과', '과태료']
    
    if any(txt in x for txt in filter_text) :
        matchings = [txt for txt in filter_text if txt in x]  
        
        for text in matchings :

            start_index = re.search(text, x).start()
            search_range = x[start_index+len(text):]
            try:
                data_type1 = r'\d{1,3},\d{3}'
                m_list = re.findall(data_type1, search_range)

                m_list_new = []
                for amt in m_list :
                    if amt.endswith('0') :
                        fine = int(''.join(re.findall('\d+', amt)))
                    else :
                        fine = None
                    m_list_new.append(fine)
                    
                if len(m_list_new) >= 2 :
                    if (max(m_list_new) - min(m_list_new))/max(m_list_new) > 0.2 :
                        return max(m_list_new)
                    else : return min(m_list_new)
                else :
                    return m_list_new[0]                   
            except:
                next

            try : 
                data_type2 = [r'\d{3,6}\s?원?', r'\d{1,3}\s?만원']
                for data in data_type2:
                    for tx in x[start_index+len(text):].strip().split(' ')[0:2] :
                        if int(tx.replace('만원', '').replace('원', '').strip()) :
                            m = re.search(data, tx).group()                       
                            if '만원' in m:
                                return int(''.join(re.findall('\d+', m)))*10000
                            else:
                                m_num = int(''.join(re.findall('\d+', m)))
                                if m_num%10 == 0 & m_num < 3000000 :
                                    return int(m_num)
                                else :
                                    return None    
            except :
                next
        return None    

    else:
        data_type3 = [r'\d{1,3},\d{3}', r'\d{3,6}\s?원', r'\d{1,3}\s?만원'] # 금액 기준의 Data 가져오기

        for data in data_type3:
            try :
                m_list = re.findall(data, x)
                # m_list_new = []
                for amt in m_list :
                    if int(amt.replace('만원', '').replace('원', '').replace(',', '').strip()) :
                        if '만원' in amt:
                            fine = int(''.join(re.findall('\d+', amt)))*10000
                            return fine
                        else :
                            fine = int(''.join(re.findall('\d+', amt)))
                            if fine%10 == 0 & fine < 1000000 :
                                return fine
            except :
                next
    return None

# 위반장소 추출

def get_place(x):
    filter_text = ['위반장소', '단속장소', '위반 장소']
    if any(a in x for a in filter_text):
        for word in filter_text:
            try:
                start_index = re.search(word, x).start()
                return ' '.join(x[start_index+len(word):].split(' ')[0:])

            except:
                continue

    else:
        return None

# 위반내용 추출

def get_title(x):
    filter_text = ['위반내용', '내 용', '위반 내용']
    if any(a in x for a in filter_text):

        for word in filter_text:
            try:
                start_index = re.search(word, x).start()
                if re.search('적용', x):
                    return ' '.join(x[start_index+len(word):re.search('적용', x).start()-1].split(' ')[0:])
                else:
                    return ' '.join(x[start_index+len(word):].split(' ')[0:])

            except:
                continue

    else:
        return None

# 부과 기관장 추출

def officer_title(x, single_office_cd):
    abstract_text = {'경남' : '경상남도', '경북' : '경상북도','전남':'전라남도','전북' : '전라북도','충남':'충청남도','충북':'충청북도','경기' : '경기도', '서울' : '서울특별시','제주':'제주도특별자치도', '세종특별시':'세종특별자치시',
                    '강원' : '강원도', '인천' : '인천광역시', '부산':'부산광역시', '대구':'대구광역시', '대전': '대전광역시', '광주':'광주광역시', '울산':'울산광역시'}
    single_office_cd = list(filter(lambda x : len(x) > 1 , single_office_cd))
    single_office_cd.remove('서울특별시')

    for txt in single_office_cd :
        if txt in x :
            return (txt, 'S')  #독립적인 조직명 single 
    
    reg_type = [r'(광주순환|광주제2순환)[가-힣]+\s?[가-힣]+영업소', r'[가-힣]+(광역시장|특별시장)',r'([가-힣]+시)\s?([가-힣]+구청장)', r'[가-힣]+시장', r'[가-힣]+군수',  r'[가-힣]+구청장',  r'[가-힣]+구청', r'[가-힣]+소장']

    for data in reg_type:
        try:
            officers = re.search(data, x).group()
            if len(officers.split(' ')) == 1 :
                office_reg = [r'([가-힣]+(특별시|광역시)[가-힣]+(청장))', r'([가-힣]+(시)[가-힣]+(소장))']
                for reg in office_reg:
                    try :
                        match_word = max(re.findall(reg, officers)[0], key=len)
                        print(match_word)
                        split_txt = ['특별시','광역시','시']
                        for txt in split_txt :
                            try :
                                temp_idx = re.search(txt, match_word).start()
                                new_officer = match_word[0:temp_idx+len(txt)] + ' ' + match_word[temp_idx+len(txt):]
                                return (new_officer, 'M')
                            except :
                                next
                    except :
                       next 
                return (officers, 'M')
            else :
                return (officers, 'M')
        except :
            next
    return (None, None)

    





# 부과기관 추출
def extract_official_adds(df_new) :
    y_min = min(df_new['y_upper'])
    y_max = max(df_new['y_lower'])
    x_max = max(df_new['x_left'])

    df_office = df_new[df_new['x_left'] <= int(x_max/3)]
    df_office = df_office[df_office['y_upper'] <= int((y_max-y_min)/6)]

    # print(df_office)
    # 본사 주소 제외
    try:
        exclude_text = ['서울특별시', '인천광역시', '미추홀구', '미래에셋', '주안동', '을지로5길', '대우증권']
        exclude_offc = df_office[['x_left', 'y_upper']][(df_office['inferText'].isin(exclude_text)) & (df_office['x_left'] >= 350)]
        exclude_x = min(exclude_offc['x_left'])
        exclude_y = min(exclude_offc['y_upper'])

        df_office = df_office[(df_office['x_left'] <= exclude_x-20) & (df_office['y_upper'] <= exclude_y-20)]
    except:
        pass

    office_parsing_list = df_office['inferText'].to_list()
    full_text = ' '.join(office_parsing_list)
    
    except_list = ['경기도 의정부시 청사로 1'] # 경기도 처럼 같은 포맷의 통지서 쓰는 기관 예외처리
    for txt in except_list :
        full_text = full_text.replace(txt, '')

    adds_type = r'((([가-힣]+(시|도))|(경남|경북|전남|전북|충남|충북|경기|서울|제주))+\s?([가-힣]+(군|구|시|로))+\s?([가-힣]+(구|소))?)'
    # adds_type = r'(([가-힣]+(시|도))|(경남|경북|전남|전북|충남|충북|경기|서울|제주))+'
    #_________________________________________________________________________________________#
    # 상기 regular expression은 2개의 블럭으로 되어 있어 리스트내 2개의 Tuple로 값 반환하므로 변경 시 아래 List Comprehension 변경 필요 ##
    try:
        add_set = []
        adds_list = []
        for t in re.findall(adds_type, full_text) :
            for a in t :
                if len(a) > 1 :
                    adds_list.append(a.strip())

        for add in adds_list :
            if len(add.split(' ')) == 3 :
                if add.split(' ')[0][-1] == add.split(' ')[1][-1] : # 첫번째랑 두번째 끝이 같을 때 (ex 서울특별시 서울시)
                    new_add = add.replace(add.split(' ')[1], '').strip()
                    add_set.append(new_add)
                elif add.split(' ')[1][-1] == add.split(' ')[2][-1] : # 두번째랑 세번째 끝이 같을 때 (ex 서울특별시 서울시)
                    new_add = ' '.join(add.split(' ')[0:2]).strip()
                    add_set.append(new_add)
                elif add.split(' ')[2][-1] == '로' :
                    new_add = ' '.join(add.split(' ')[0:2]).strip()
                    add_set.append(new_add)
                elif add.split(' ')[1][-1] == '군' : # 두번째가 군일 때 뒤에 오는 것 삭제
                    new_add = ' '.join(add.split(' ')[0:2]).strip()
                    add_set.append(new_add)
                else :
                    add_set.append(add)

            elif len(add.split(' ')) == 2 :
                if add.split(' ')[0][-1] == add.split(' ')[1][-1] :
                    new_add = add.replace(add.split(' ')[1], '').strip()
                    add_set.append(new_add)
                elif add.split(' ')[1][-1] == '로' :
                    new_add = add.replace(add.split(' ')[1], '').strip()
                    add_set.append(new_add)
                else :
                    add_set.append(add)
                
            else :
                if add[-1] == '로' :
                    new_add = add.replace(add, '').strip()
                    add_set.append(new_add)
                elif re.search(r'[가-힣]+(도|특별시|광역시)[가-힣]+(시|군|구)', add) :
                    split_txt = ['도','특별시','광역시']
                    for txt in split_txt :
                        try :
                            temp_idx = re.search(txt, add).start()
                            new_add = add[0:temp_idx+len(txt)] + ' ' + add[temp_idx+len(txt):]
                            add_set.append(new_add)
                        except :
                            next
                    else :
                        next
                else :
                    add_set.append(add)

        new_add_set = set(add_set)
        new_add_set_f = max(new_add_set, key=len)
        offical_adds = change_officeName(new_add_set_f)
        return offical_adds, full_text, new_add_set

    except:
        return None, full_text, None

def naver_general_ocr(image_files) :
    raw_data = {}

    for image_file in image_files :

        file_key = Path(image_file).stem
        secret_key = 'elFDaGx5dm5SSWhjYnREQWFvSUJ6ckFxWXJ6dWJhWGg='
        api_url ='https://29280af484d34729ada88dcd3bbbfe3a.apigw.ntruss.com/custom/v1/6541/9f24228aa50496e90ee3a097e0fd65f27057b9a66468c1c7b5de681d2a39f137/general'

        request_json = {
            'images': [
                {
                    'format': 'jpg',
                    'name': 'demo'
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        payload = {'message': json.dumps(request_json).encode('UTF-8')}
        files = [
        ('file', open(image_file,'rb'))
        ]
        headers = {
        'X-OCR-SECRET': secret_key
        }

        response = requests.request("POST", api_url, headers=headers, data = payload, files = files, verify = False)
        data = response.json()

        raw_data[file_key] = data

    return raw_data

def mapping_wetax(ocr_df, refined_wetax_df) :
    # 전자납부번호 있는 df 필터 및 mapping
    # 위택스 컬럼정보 ['taxed_office', '과목명', '부과구분', 'car_reg_num', 'violated_time', 'due_date', 'violated_place', '전자납부번호', '부과금액','가산금액', '납부금액', '신고납부관할지', 'total_text']
    # OCR 결과 컬럼정보 [official_adds, office_in_charge_f, car_reg_num, elec_invoice, violated_date, time_type, due_date, taxation_number, due_amount, violated_place, violated_content, taxation_officer, officer_cls, refer_text_total, office_adds_list]
    ocr_df['violated_date'] = ocr_df['violated_date'].dt.strftime('%Y%m%d%H%M%S')
    ocr_df['due_date'] = ocr_df['due_date'].dt.strftime('%Y%m%d%')
    
    df_elecInvoice = ocr_df[~ocr_df['elec_invoice'].isnull()]
    
    first_mapped_df = pd.merge(df_elecInvoice, refined_wetax_df, left_on = 'elec_invoice', right_on = '전자납부번호', how='left')
    
    refined_wetax_second = refined_wetax_df[(~refined_wetax_df['car_reg_num_wetax'].isnull()) & (~refined_wetax_df['violated_time'].isnull())]
    ocr_nonNull = ocr_df[(~ocr_df['car_reg_num'].isnull()) & (~ocr_df['violated_date'].isnull())]
    second_mapped_df = pd.merge(ocr_nonNull, refined_wetax_second, left_on = ['car_reg_num', 'violated_date'], right_on = ['car_reg_num_wetax', 'violated_time'], how='left')

    common_cols = ['index', 'official_adds', 'office_in_charge', 'taxation_officer', 'office_adds_list', 'officer_cls', 'car_reg_num', 'elec_invoice', 'violated_date', 'time_type', 'due_date', 'taxation_number', 'due_amount', 'violated_place', 'violated_content',  'refer_text_total', 'taxed_office', '과목명', '부과구분', 'car_reg_num_wetax', 'violated_time', 'due_date_wetax', 'violated_place_wetax', '전자납부번호', '부과금액','가산금액', '납부금액', '신고납부관할지', 'total_text']
    first_mapped_df = first_mapped_df[common_cols]
    second_mapped_df = second_mapped_df[common_cols]

    combined_df = pd.concat([first_mapped_df, second_mapped_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(['car_reg_num','violated_date'],keep= 'first')
    combined_df.insert(4, '기관명', '')

    # 겹치지 않는 데이터프레임 추출
    df1[~df1.apply(tuple,1).isin(df2.apply(tuple,1))]

    return combined_df


def refine_wetax(wetax_df) :

    wetax_df['total_text'] = wetax_df['과세대상'].fillna('/')+'/'+ wetax_df['위반항목1'].fillna('/')+'/'+ wetax_df['위반항목2'].fillna('')

    def violation_time_wetax(x):
        date_type = [r'\d{4}\s?[-./]?\s?\d{1,2}\s?[-./]?\s?\d{1,2}\s?\d{1,2}\s?:?\s?\d{1,2}\s?:?\s?\d{2}?', r'\d{4}년\d{1,2}월\d{1,2}일\s?\d{2}시\d{2}분', r'\d{2,4}[-./]\d{1,2}[-./]\d{1,2}\s?\d{1,2}:\d{1,2}',
                    r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}\s?\d{1,2}\s?:\s?\d{1,2}', r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}']

        for dt_type in date_type:
            try:
                date_text = re.search(dt_type, x).group().replace(' ', '')
                return make_date(date_text)
            except:
                continue
        return None

    def get_place_wetax(x):
        filter_text = ['위반장소', '단속장소', '위반 장소']
        for txt in x.split(sep = '/') :
            if any(a in txt for a in filter_text):
                for word in filter_text:
                    try:
                        start_index = re.search(word, txt).start()
                        return txt[start_index+len(word)+1:]
                    except:
                        next    
            else :
                next
        return None

    wetax_df['car_reg_num_wetax'] = wetax_df.apply(lambda x : x['차량 번호'] if x['차량 번호'] is not None else get_carNum(x['total_text']), axis = 1)
    wetax_df['violated_time'] = wetax_df['total_text'].apply(violation_time_wetax)
    wetax_df['violated_time'] = wetax_df['violated_time'].dt.strftime('%Y%m%d%H%M%S')
    wetax_df['due_date_wetax'] = wetax_df['납기일자'].apply(violation_time_wetax)
    wetax_df['due_date_wetax'] = wetax_df['due_date_wetax'].dt.strftime('%Y%m%d')
    wetax_df['violated_place_wetax'] = wetax_df['total_text'].apply(get_place_wetax)
    wetax_df['taxed_office'] = wetax_df['신고납부관할지'].apply(change_officeName)    
    new_wetax = wetax_df[['taxed_office', '과목명', '부과구분', 'car_reg_num_wetax', 'violated_time', 'due_date_wetax', 'violated_place_wetax', '전자납부번호', '부과금액','가산금액', '납부금액', '신고납부관할지', 'total_text']]

    return new_wetax


def main_process(data, div_cd, single_office_cd) :

    fields = ["inferText", "lineBreak", "boundingPoly.vertices"]
    df = pd.json_normalize(data['images'][0]['fields'])
    df_filter = df[fields].copy()

    df_filter.loc[:, 'x'] = df_filter["boundingPoly.vertices"].apply(lambda x: [x[i]['x'] for i in range(4)])
    df_filter.loc[:, 'y'] = df_filter["boundingPoly.vertices"].apply(lambda x: [x[i]['y'] for i in range(4)])

    df_parsed = df_filter[['inferText', 'lineBreak',  'x', 'y']].copy()
    df_parsed['담당과'] = df_parsed.apply(lambda x: office_inCharge(x['inferText'], div_cd), axis=1) 
    df_parsed['차량번호'] = df_parsed['inferText'].apply(get_carNum)
    df_parsed['전자납부번호'] = df_parsed['inferText'].apply(get_elecInvoice)


    office_in_charge = set(df_parsed['담당과'][~df_parsed['담당과'].isnull()])
    new_list = full_context(df_parsed)
    df_new = pd.DataFrame(new_list, columns=['inferText', 'x_left', 'x_right', 'y_upper', 'y_lower'])

    # 유료도로 여부 header 찾기
    toll_words = ['유료', '유료도로', '유료도로법', '유료고속도로', '미납통행', '통행료', '주차요금']
    df_new['유료도로여부'] = df_new['inferText'].apply(lambda x: 'Y' if any(a in x for a in toll_words) else '')
    df_new['지로여부'] = df_new['inferText'].apply(lambda x: 'Y' if any(a in x for a in ['지로', '지로번호']) else '')

    # 교통범칙금 여부 header 찾기
    traffic_words = ['주·정차위반', '주.정차위반', '도로교통법', '제32조', '주정차위반', '주정차 위반']
    df_new['도로교통법여부'] = df_new['inferText'].apply(lambda x: 'Y' if any(a in x for a in traffic_words) else '')

    toll_yn = ('Y' if 'Y' in df_new['유료도로여부'].unique() else 'N')
    df_new['위반일시'] = df_new.apply(lambda x: violation_time(x['inferText'], toll_yn), axis=1)
    df_new['납부기한'] = df_new.apply(lambda x: due_dates(x['inferText'], toll_yn), axis=1)
    df_new['차량번호'] = df_new['inferText'].apply(get_carNum)
    df_new['전자납부번호'] = df_new['inferText'].apply(get_elecInvoice)
    df_new['납세번호'] = df_new['inferText'].apply(get_taxation)
    df_new['납부금액'] = df_new['inferText'].apply(get_amount)
    df_new['위반장소'] = df_new['inferText'].apply(get_place)
    df_new['위반내용'] = df_new['inferText'].apply(get_title)
    df_new['부과기관장'] = df_new.apply(lambda x: officer_title(x['inferText'], single_office_cd)[0], axis=1) 
    df_new['기관장구분'] = df_new.apply(lambda x: officer_title(x['inferText'], single_office_cd)[1], axis=1) 
    # df_new['담당과'] = df_new.apply(lambda x: office_inCharge(x['inferText'], div_cd), axis=1) 


    # trigger point
    ocr_trigger = min(df_new['y_upper'][df_new['inferText'].str.contains('OCR')], default=0)-50
    content_trigger = (max(df_new['y_lower'], default=0) - min(df_new['y_upper'], default=0))/3

    # print(df_new['위반일시'].unique(), '\n', df_new['납부기한'].unique(), '\n', df_new['차량번호'].unique(), '\n', df_new['전자납부번호'].unique(), '\n', df_new['납세번호'].unique(
    # ), '\n', df_new['납부금액'].unique(), '\n', df_new['위반장소'].unique(), '\n', df_new['위반내용'].unique(), '\n', df_new['부과기관장'].unique())

    # print(df_parsed[~df_parsed['차량번호'].isnull()])
    # print(df_parsed[~df_parsed['전자납부번호'].isnull()])

    # 최종 차량번호 추출
    try :
        car_reg_num_series = df_parsed['차량번호'][~df_parsed['차량번호'].isnull()]
        car_reg_num_series_t = df_new['차량번호'][~df_new['차량번호'].isnull()]
        car_reg_num_df = pd.concat([car_reg_num_series, car_reg_num_series_t]).reset_index(drop=True)
        # car_reg_num_df = car_reg_num_series.groupby('inferText').sum().add(car_reg_num_series_t.groupby('inferText').sum(), fill_value=0).reset_index()
        car_reg_num_s = car_reg_num_df.value_counts(ascending = False)
        car_reg_num = car_reg_num_s.index[0]
    except : car_reg_num = None

    # 최종 전자납부번호 추출
    try :
        elec_invoice_series = df_parsed.groupby('전자납부번호')['inferText'].count().sort_values(ascending = False)
        elec_invoice_series_new = df_new.groupby('전자납부번호')['inferText'].count().sort_values(ascending = False)
        elec_invoice_df = pd.concat([elec_invoice_series, elec_invoice_series_new], axis = 1)
        elec_invoice = ''.join(re.findall('\d+', elec_invoice_df.index[0]))
    except : elec_invoice = None

    # 납부기한 추출
    try :
        df_dueDate = df_new['납부기한'][~df_new['납부기한'].isnull()]
        due_date_list = list(filter(lambda x : x <= datetime.today() + timedelta(days = 90), df_dueDate))
        due_date = max(due_date_list)
    except : due_date = None

    # 위반일시 추출
    try :
        df_violatedDate = df_new['위반일시'][~df_new['위반일시'].isnull()]
        if due_date is not None :
            violated_dates_list = list(filter(lambda x : x < due_date, df_violatedDate))
            # violated_dates = df_violatedDate[df_violatedDate['위반일시'] < due_date]
        else :
            violated_dates_list = list(df_violatedDate)

        violated_dates_df = pd.DataFrame(violated_dates_list, columns = ['위반일시'])
        violated_dates_df['구분'] = violated_dates_df['위반일시'].apply(lambda x : 0 if isinstance(x, date) else 1)
        violated_dates_gb = violated_dates_df.groupby('위반일시')['구분'].count().reset_index(name="count")
        violated_dates_gb['구분'] = violated_dates_gb['위반일시'].apply(lambda x : 0 if (x.hour == 0) & (x.minute == 0) else 1)
        violated_dates = violated_dates_gb.sort_values(['구분', '위반일시'], ascending = [False, True])
        
        if toll_yn == "Y" :
            violated_date = violated_dates['위반일시'].to_list()[0]
        else :
            violated_date = violated_dates['위반일시'].value_counts().index[0]

    except : violated_date = None

    # 납세번호 추출
    try :
        df_taxation = df_new['납세번호'][~df_new['납세번호'].isnull()]
        taxation_number = df_taxation[0]
    except : taxation_number = None

    # 부과금액
    try :
        if ocr_trigger != None :
            df_dueAmount = df_new[['납부금액', 'inferText']][(~df_new['납부금액'].isnull()) & (df_new['y_lower'] > content_trigger)]
        else :
            df_dueAmount = df_new[['납부금액', 'inferText']][(~df_new['납부금액'].isnull()) & (df_new['y_lower'] > ocr_trigger)]

        def tagging(x) :
            filter_text = {'합계금액' : 10, '총합계' : 10, '합 계' : 10, '감경금액' : 10, '납기내 금액' : 10, '납부금액 (20%감경금액)' : 10, '감경20%' : 10, '기한내' : 10, '기한 내' : 10, '납부액' : 9, '납부금액' : 10, '과태료금액' : 5, '과태료' : 5, '본금액' : 0, '금액' : 7, '금 액' : 7, '부과' : 5, '가산금예정' : -10}
            for k, v in filter_text.items() :
                if k in x :
                    return v
                else :
                    continue
            return 0
        
        def Ordering(df) :
            df_new = df.sort_values(['우선', '구분'], ascending = [False, False])
            if df_new.shape[0] >= 2 :
                if (max(df_new.index[0:1]) - min(df_new.index[0:1]))/max(df_new.index[0:1]) == 0.2 :
                    return min(df_new.index[0:1])
                else :
                    return df_new.index[0]
            else :
                return df_new.index[0]

       
        df_dueAmount['구분'] = df_dueAmount['inferText'].apply(tagging)
        if car_reg_num :
            df_dueAmount['구분'] = df_dueAmount.apply(lambda x : -10 if x['납부금액'] == int(car_reg_num[-4:]) else x['구분'], axis=1)

        df_dueAmount['우선'] = df_dueAmount['구분'].apply(lambda x : 1 if x == 10 else 0)
        
        df_dueAmount_temp = df_dueAmount.copy().reset_index(drop = True)
        df_dueAmount_f = df_dueAmount_temp.groupby('납부금액').agg({'구분' : 'sum', '우선' : 'sum'})

        due_amount = Ordering(df_dueAmount_f)
        
    except : due_amount = None

    # 위반장소 추출
    try :
        violated_place_df = df_new['위반장소'][~df_new['위반장소'].isnull()].to_list()
        violated_place_df.sort(key=len)
        violated_place = violated_place_df[0].replace(':', '').strip()
    except : violated_place = None

    # 위반내용 추출
    try :
        violated_content_df = df_new['위반내용'][~df_new['위반내용'].isnull()].to_list()
        violated_content_df.sort(key=len)
        violated_content_t = violated_content_df[0].replace(':', '').strip()
        filter_text = ['부근', '인근']
        for txt in filter_text :
            try :
                start_index = violated_content_t.find(txt)
                violated_content = violated_content_t[0: start_index+len(txt)]
            except :
                next
        violated_content = violated_content_t
    except : violated_content = None

    # 부과기관장 추출
    try :   
        df_officer = df_new['부과기관장'][~df_new['부과기관장'].isnull()]
        taxation_officer_s = df_officer.value_counts(ascending = False)
        count_list = list(taxation_officer_s.values)
        if count_list.count(count_list[0]) == len(count_list) :
            taxation_officer_s.index.str.len().sort_values(ascending = True)
            taxation_officer = taxation_officer_s.index[0]
        else :
            taxation_officer = taxation_officer_s.index[0]
    except :
        taxation_officer = None
    
    # 기관장 구분 추출
    if taxation_officer is not None :
        officer_cls = df_new['기관장구분'][df_new['부과기관장'] == taxation_officer].values[0]
    else :
        officer_cls = None

    # 담당과 추출
    office_in_charge_f = office_in_charge.pop() if len(office_in_charge) > 0 else ''

    # 부과기관 주소 추출
    official_adds, full_text, office_adds_set = extract_official_adds(df_new)  # 부과기관 주소, 표지페이지 Full text, 부과기관명 Set 가져오기

    # 기관코드 추출을 위한 통합 Data Set
    def revise_end_words(x, officer_cls) :
        if officer_cls == 'M' :
            x.strip()
            if x.endswith('시장') : return x[0:-1]
            elif x.endswith('구청장') : return x[0:-2]
            elif x.endswith('군수') : return x[0:-1]
            elif x.endswith('구청') : return x[0:-1]
            elif x.endswith('출장소장') : return x[0:-1]
            else : return x
        else : return x

    revised_tax_officer = revise_end_words(taxation_officer, officer_cls)
    print(revised_tax_officer)
    office_adds_list = []
    if office_adds_set :
        office_adds_list.append(list(office_adds_set))
        office_adds_list.append(office_in_charge_f)
        office_adds_list.append(revised_tax_officer)
    else :
        office_adds_list.append(office_in_charge_f)
        office_adds_list.append(revised_tax_officer)


    # 위반일시의 Time형식 여부 추출
    try :
        time_type = 'Y' if not (violated_date.hour or violated_date.minute or violated_date.second) else 'N'
    except :
        time_type = 'N'

    # 참고 Text 합성
    def hms(x) :
        try :
            return re.search(r'\d{1,2}\s?:\s?d{1,2}\s?:\s?d{1,2}', x).group().replace(' ', '')
        except :
            return None

    df_refer = df_new[['inferText', '차량번호', '전자납부번호', '납세번호', '위반일시', '위반장소', '위반내용', '납부기한', '납부금액', '부과기관장']]
    df_refer['시분초'] = df_refer['inferText'].apply(hms) # 시분초 형태가 있는 row 추가
    df_refer = df_refer.astype(object).where(pd.notnull(df_refer),None)
    refer_text = []

    for k, v in df_refer.iterrows() :
        cnt = 0
        for vv in v[1:] :
            if vv is not None :
                cnt +=1
        if cnt > 0 :
            refer_text.append(str(v[0]))

    refer_text_total = '\n'.join(refer_text)
    print(official_adds, office_in_charge_f, car_reg_num, elec_invoice, violated_date, time_type, due_date, taxation_number, due_amount, violated_place, violated_content, taxation_officer, officer_cls, office_adds_list)

    return [official_adds, office_in_charge_f, car_reg_num, elec_invoice, violated_date, time_type, due_date, taxation_number, due_amount, violated_place, violated_content, taxation_officer, officer_cls, refer_text_total, office_adds_list]


def main():
    global working_date
    working_date = datetime.today().strftime('%Y%m%d%H%M')
    
    with open(r'src\constants.json') as json_file:
        json_data = json.load(json_file)
    paths_to_handle = make_folder(json_data)    
    
    # ocr 대상 tiffs 파일 읽어서 jpg로 쪼개고 tiff 파일 지우기
    # tiffs_files = getListOfFiles(paths_to_handle[0])
    # split_tiffs(tiffs_files, paths_to_handle[2])

    # daily_working_path_tiff = os.path.join(paths_to_handle[8], working_date[0:8]) 
    # if not os.path.isdir(daily_working_path_tiff):                                                           
    #     os.mkdir(daily_working_path_tiff)

    # for i, files in enumerate(tiffs_files) :
    #     renamed_raw = 'tiff_image_files_{}_{}'.format(working_date, i)
    #     os.rename(files, os.path.join(daily_working_path_tiff, renamed_raw))

    # print("Tiffs to jpgs splitted complete!")
    
    # ocr_jpg_files = glob.glob(paths_to_handle[2]+'*.jpg')
    
    # parsed_data = naver_general_ocr(ocr_jpg_files)
    # print("Naver General OCR Raw Data Parsed!!")

    # daily_working_json_path = os.path.join(paths_to_handle[11], working_date[0:8]) 
    # if not os.path.isdir(daily_working_json_path):                                                           
    #     os.mkdir(daily_working_json_path)
    # json_file_name = 'general_ocr_results_json_{}.json'.format(working_date[0:12])
    
    # with open(os.path.join(daily_working_json_path, json_file_name), 'w', encoding='utf-8') as f :
    #     json.dump(parsed_data, f, indent=4)
    # print("Naver General OCR Raw Data Saved as JSON Format!!")

    # 임시 테스트
    with open(r'rsc\templates_rawData.json', encoding='utf-8') as json_file:
        parsed_data = json.load(json_file)
    
    office_cd = pd.read_csv(r'src\office_codes.csv', delimiter = '\t', encoding = 'utf-8', dtype = {'관청코드' : str})
    div_cd = office_cd['관청명(시군구)'].apply(lambda x: x.split(' ')[-1]).unique().tolist()
    single_office_cd = office_cd['관청명(시군구)'].apply(lambda x: x.split(' ')[0] if len(x.split(' '))==1 else '').unique().tolist()

    total_dict = {}
    for k, v in parsed_data.items() :
        if k == '전라남도_장흥군_재난안전과_16너4784_20210725153100' :
            result_set = main_process(v, div_cd, single_office_cd)
            total_dict[k] = result_set
    print("Fine Data Extracted!!")

    df_final = pd.DataFrame(total_dict.values(), index = total_dict.keys(), columns = ['official_adds', 'office_in_charge', 'office_adds_set', 'car_reg_num', 'elec_invoice', 'violated_date', 'time_type', 'due_date', 'taxation_number', 'due_amount', 'violated_place', 'violated_content', 'taxation_officer', 'officer_class', 'refer_text_total']).reset_index()

    # df_final.to_excel(r'output\ocr_result_xls\test_xls.xlsx')
    # 위택스 매핑
    # df_wetax = pd.read_csv(r'rsc\wetax.csv', delimiter = '\t', encoding = 'utf-8', dtype = {'전자납부번호' : str})
    # refinded_wetax = refine_wetax(df_wetax)
    # mapped_df = mapping_wetax(df_final, refinded_wetax)
    
    # daily_working_path = os.path.join(paths_to_handle[7], working_date[0:8]) 
    # if not os.path.isdir(daily_working_path):                                                           
    #     os.mkdir(daily_working_path)

    # xlsx_file_name = "naver_general_ocr_result_" + working_date + '.xlsx'
    # mapped_df.to_excel(os.path.join(daily_working_path, xlsx_file_name), index=False)

    print("Excel File Saved!!")

if __name__ == '__main__':
    main()
