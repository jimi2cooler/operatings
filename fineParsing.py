import datetime
from datetime import datetime, timedelta
import json, re, glob
from os import error
from pathlib import Path
import pandas as pd
import numpy as np
import scipy.spatial.distance as distance
 
def sorting_bounding_box(points):
    
    points = list(map(lambda x:[x[0],x[1][0],x[1][2]],points))
    
    points_sum = list(map(lambda x: [x[0],x[1],sum(x[1]),x[2][1]],points))
    x_y_cordinate = list(map(lambda x: x[1],points_sum))
    final_sorted_list = []
    while True:
        try:
            new_sorted_text = []
            initial_value_A  = [i for i in sorted(enumerate(points_sum), key=lambda x:x[1][2])][0]
    #         print(initial_value_A)
            threshold_value = abs(initial_value_A[1][1][1] - initial_value_A[1][3])
            threshold_value = (threshold_value/2) + 5
            del points_sum[initial_value_A[0]]
            del x_y_cordinate[initial_value_A[0]]
    #         print(threshold_value)
            A = [initial_value_A[1][1]]
            K = list(map(lambda x:[x,abs(x[1]-initial_value_A[1][1][1])],x_y_cordinate))
            K = [[count,i]for count,i in enumerate(K)]
            K = [i for i in K if i[1][1] <= threshold_value]
            sorted_K = list(map(lambda x:[x[0],x[1][0]],sorted(K,key=lambda x:x[1][1])))
            B = []
            points_index = []
            for tmp_K in sorted_K:
                points_index.append(tmp_K[0])
                B.append(tmp_K[1])
            dist = distance.cdist(A,B)[0]
            d_index = [i for i in sorted(zip(dist,points_index), key=lambda x:x[0])]
            new_sorted_text.append(initial_value_A[1][0])

            index = []
            for j in d_index:
                new_sorted_text.append(points_sum[j[1]][0])
                index.append(j[1])
            for n in sorted(index, reverse=True):
                del points_sum[n]
                del x_y_cordinate[n]
            final_sorted_list.append(new_sorted_text)
            # print(new_sorted_text)
        except Exception as e:
            print(e)
            break

# example points
points = [['11/10,', [[466.66666, 261.33334],
    [532.     , 261.33334],
    [532.     , 285.33334],
    [466.66666, 285.33334]]],
    ['st', [[556.     , 261.33334],
    [582.6667 , 261.33334],
    [582.6667 , 285.33334],
    [556.     , 285.33334]]], ['Str', [[586.6667 , 261.33334],
    [626.6667 , 261.33334],
    [626.6667 , 285.33334],
    [586.6667 , 285.33334]]], ['R', [[377.33334, 262.66666],
    [400.     , 262.66666],
    [400.     , 285.33334],
    [377.33334, 285.33334]]], ['si.', [[410.66666, 264.     ],
    [442.66666, 264.     ],
    [442.66666, 285.33334],
    [410.66666, 285.33334]]], ['1.', [[544.     , 264.     ],
    [561.3333 , 264.     ],
    [561.3333 , 285.33334],
    [544.     , 285.33334]]], ['et,', [[637.3333, 264.    ],
    [670.6667, 264.    ],
    [670.6667, 288.    ],
    [637.3333, 288.    ]]], ['et', [[396.     , 265.33334],
    [414.66666, 265.33334],
    [414.66666, 285.33334],
    [396.     , 285.33334]]], ["'el", [[622.6667 , 265.33334],
    [641.3333 , 265.33334],
    [641.3333 , 285.33334],
    [622.6667 , 285.33334]]], ['in', [[529.3333 , 276.     ],
    [537.3333 , 276.     ],
    [537.3333 , 285.33334],
    [529.3333 , 285.33334]]], ['Corporati', [[378.73196, 287.75485],
    [482.9534 , 289.35825],
    [482.57034, 314.25494],
    [378.3489 , 312.65155]]], ['ion', [[478.66666, 288.     ],
    [518.6667 , 288.     ],
    [518.6667 , 309.33334],
    [478.66666, 309.33334]]], ['Colony,', [[525.82104, 285.5305 ],
    [614.4748 , 291.07132],
    [613.00653, 314.5629 ],
    [524.3528 , 309.02206]]], ['T.Nafgg,', [[377.85098, 309.27054],
    [470.8392 , 316.4235 ],
    [468.88623, 341.81174],
    [375.89804, 334.65878]]], ['Chennai', [[476.     , 313.33334],
    [566.6667 , 313.33334],
    [566.6667 , 336.     ],
    [476.     , 336.     ]]], ['48.', [[592.     , 313.33334],
    [626.6667 , 313.33334],
    [626.6667 , 334.66666],
    [592.     , 334.66666]]]]


# 담당과 찾기
def office_inCharge(x):
    reg_x = r'(([가-힣])*(주차|관리|교통|장애|복지|차량|행복|가정|청소|가로|정비|경제|안전|노인|위생|환경|도시|버스|민원)+([가-힣]+)?(과|단))'
    try:
        return re.search(reg_x, x).group()
    except:
        return None

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
            return pd.to_datetime(num_text, format='%Y%m%d%H%M%S', errors='ignore')
        elif 10 <= len(num_text) <= 12:
            if num_text.startswith('20') :
                return pd.to_datetime(num_text, format='%Y%m%d%H%M', errors='ignore')
            else :
                return pd.to_datetime(num_text, format='%y%m%d%H%M', errors='ignore')
        elif 6 <= len(num_text) <= 9:
            return pd.to_datetime(num_text, format='%Y%m%d', errors='ignore')
        elif len(num_text) < 6:
            return pd.to_datetime(num_text, format='%Y%m%d', errors='ignore')
        else:
            return pd.to_datetime(num_text, format='%c', errors='ignore')
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

        date_type = [r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}\s?\s?\d{1,2}\s?:\s?\d{2}\s?:\s?\d{2}', r'\d{4}년\d{1,2}월\d{1,2}일\s?\d{2}시\d{2}분', r'\d{2,4}[-./]\d{1,2}[-./]\d{1,2}\s?\d{1,2}:\d{1,2}',
                     r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}\s?\d{1,2}\s?:\s?\d{1,2}$', r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}']

        for dt_type in date_type:
            try:
                date_text = re.search(
                    dt_type, x_adj).group().replace(' ', '')
                return make_date(date_text)
            except:
                continue
        return None

    else:

        if any(a in x for a in ['위반 ', '위반일시', '주차일시', '주차', '위반 일시', '단속일시']):

            # 혼잡통행료 예외 처리 (일자 데이터 사이 차량번호 제거)
            car_num_type = re.search(r'\d{2,3}\s?[ㄱ-ㅎ가-힣]{1}\s?\d{4}\s', x)
            if car_num_type:
                x_adj = x.replace(car_num_type.group(), '')
            else:
                x_adj = x

            date_type = [r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}\s?\s?\d{1,2}\s?:\s?\d{2}\s?:\s?\d{2}', r'\d{4}년\s?\d{1,2}월\s?\d{1,2}일\s?\d{2}시\s?\d{2}분', r'\d{4}-\d{1,2}-\d{1,2}\s?\d{1,2}:\d{1,2}',
                         r'\d{4}\s?[-./]\s?\d{1,2}\s?[-./]\s?\d{1,2}\s?\d{1,2}\s?:\s?\d{1,2}']

            for dt_type in date_type:
                try:
                    date_text = re.search(
                        dt_type, x_adj, re.IGNORECASE).group().replace(' ', '')
                    return make_date(date_text)
                except:
                    continue

        else:
            return None

# 납부기한 추출

def due_dates(x):
    filter_after = ['기한 ', '납부기한', '납기내', '납기일', '납부일']

    for text in filter_after:
        if text in x:
            date_type = [r'\d{4}[-./년]\s?\d{1,2}[-./월]\s?\d{1,2}[일]?']
            for dt_type in date_type:
                try:
                    start_index = re.search(text, x).start()
                    date_text = re.search(
                        dt_type, x[start_index+len(text):], re.IGNORECASE).group().replace(' ', '')
                    return make_date(date_text)
                except:
                    return None

    filter_before = ['까지']
    for text in filter_before:
        if text in x:
            date_type = [r'\d{4}[-./년]\s?\d{1,2}[-./월]\s?\d{1,2}[일]?']
            for dt_type in date_type:
                try:
                    start_index = re.search(text, x).start()
                    date_text = re.search(
                        dt_type, x[:start_index]).group().replace(' ', '')
                    return make_date(date_text)
                except:
                    return None

    else:
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
    filter_text = ['합계금액', '총합계', '합 계', '감경금액', '납기내 금액', '납부금액 (20%감경금액)', '미납요금','납부액', '납부금액', '금액', '금 액', '부과', '과태료']
    
    for text in filter_text :
        if text in x :
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
                                if m_num%10 == 0 & m_num < 1000000 :
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

def officer_title(x):

    reg_type = [r'[가-힣]+\s?주식회사', r'[a-Z]+\s?주식회사', r'[가-힣]+대교[가-힣]+?', r'([가-힣]+(순환도로|고속도로|관통도로|웨이|터널))+[가-힣]?', r'[가-힣]+\s?영업소[가-힣]+?', r'[가-힣]+(관리소|출장소|사업소)', r'[가-힣]+공사',
                r'[가-힣]+공단', r'(([가-힣]+시)\s?([가-힣]+구청장))', r'[가-힣]+시장', r'[가-힣]+군수',  r'[가-힣]+구청장',  r'[가-힣]+구청']

    for data in reg_type:
        try:
            if re.search(data, x) :
                if '미래에셋' in re.search(data, x).group() :
                    next
                else : 
                    return re.search(data, x).group()
        except:
            pass
    return None

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

    adds_type = r'((([가-힣]+(시|도))|(경남|경북|전남|전북|충남|충북|경기|서울|제주))+\s?([가-힣]+(군|구|시))+\s?([가-힣]+(구|과))?)'
    # adds_type = r'(([가-힣]+(시|도))|(경남|경북|전남|전북|충남|충북|경기|서울|제주))+'
    
    try:
        add_set = []
        adds_list = re.findall(adds_type, full_text)
        print(adds_list)
        for add in adds_list :
            for ad in add :
                if len(ad) > 1 :
                    add_set.append(ad)
        new_add_set = set(add_set)
        print(new_add_set)
        return max(new_add_set, key=len)

    except:
        return None
    # print(reg_result)
    # final_office_adds = []
    # office_adds = ''
    # if reg_result :
    #     for txt in reg_result :
    #         print(txt)
    #         for tx in txt.split(' ') :
    #             if not tx.endswith('로') :
    #                 office_adds = office_adds + ' ' + tx
    #         final_office_adds.append(office_adds)
    # return final_office_adds

    

def main_process(image_file, data) :

    img_key = Path(image_file).stem

    fields = ["inferText", "lineBreak", "boundingPoly.vertices"]
    df = pd.json_normalize(data[img_key]['images'][0]['fields'])
    df_filter = df[fields].copy()

    df_filter.loc[:, 'x'] = df_filter["boundingPoly.vertices"].apply(lambda x: [x[i]['x'] for i in range(4)])
    df_filter.loc[:, 'y'] = df_filter["boundingPoly.vertices"].apply(lambda x: [x[i]['y'] for i in range(4)])

    df_parsed = df_filter[['inferText', 'lineBreak',  'x', 'y']].copy()
    df_parsed['담당과'] = df_parsed['inferText'].apply(office_inCharge)
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
    df_new['납부기한'] = df_new['inferText'].apply(due_dates)
    df_new['차량번호'] = df_new['inferText'].apply(get_carNum)
    df_new['전자납부번호'] = df_new['inferText'].apply(get_elecInvoice)
    df_new['납세번호'] = df_new['inferText'].apply(get_taxation)
    df_new['납부금액'] = df_new['inferText'].apply(get_amount)
    df_new['위반장소'] = df_new['inferText'].apply(get_place)
    df_new['위반내용'] = df_new['inferText'].apply(get_title)
    df_new['부과기관장'] = df_new['inferText'].apply(officer_title)
    df_new['담당과'] = df_new['inferText'].apply(office_inCharge)

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
        due_date = max(df_dueDate.where(lambda x : x <= datetime.today() + timedelta(days = 90)))
    except : due_date = None

    # 위반일시 추출
    try :
        df_violatedDate = df_new[['위반일시', '납부기한']][~df_new['위반일시'].isnull()]
        df_violatedDate = df_new[~df_new['위반일시'] == np.naT]
        violated_dates = df_violatedDate[df_violatedDate['위반일시'] < due_date]
        violated_dates['구분'] = violated_dates['위반일시'].apply(lambda x : 0 if not (x.hour or x.minute or x.second) else 1)
        violated_dates = violated_dates.sort_values(['구분', '위반일시'], ascending = [False, True])
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
            filter_text = {'합계금액' : 10, '총합계' : 10, '합 계' : 10, '감경금액' : 10, '납기내 금액' : 10, '납부금액 (20%감경금액)' : 10, '감경20%' : 10, '납부액' : 9, '납부금액' : 10, '과태료금액' : 5, '과태료' : 5, '본금액' : 0, '금액' : 7, '금 액' : 7, '부과' : 5, '가산금예정' : -10}
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
        df_dueAmount['구분'] = df_dueAmount.apply(lambda x : -10 if x['납부금액'] == int(car_reg_num[-4:]) else x['구분'], axis=1)
        df_dueAmount['우선'] = df_dueAmount['구분'].apply(lambda x : 1 if x == 10 else 0)
        df_dueAmount_temp = df_dueAmount.copy().reset_index(drop = True)
        df_dueAmount_f = df_dueAmount_temp.groupby('납부금액').agg({'구분' : 'sum', '우선' : 'sum'})

        due_amount = Ordering(df_dueAmount_f)
        print(due_amount)
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
        violated_content = violated_content_df[0].replace(':', '').strip()
    except : violated_content = None

    # 부과기관장 추출
    try :   
        words_filter = ['미래에셋캐피탈주식회사', '미래에셋캐피탈 주식회사']
        df_officer = df_new['부과기관장'][(~df_new['부과기관장'].isnull()) & (~df_new['부과기관장'].isin(words_filter))]
        taxation_officer_s = df_officer.value_counts(ascending = False)
        taxation_officer = taxation_officer_s.index[0]
        print(taxation_officer)
    except :
        taxation_officer = None

    # 담당과 추출
    office_in_charge_f = office_in_charge.pop() if len(office_in_charge) > 0 else ''
    print(office_in_charge_f)

    # 부과기관 주소 추출
    official_adds = extract_official_adds(df_new)
    print(img_key, official_adds)
    # 참고 Text 합성

    df_refer = df_new[['inferText', '차량번호', '전자납부번호', '납세번호', '위반일시', '위반장소', '위반내용', '납부기한', '납부금액', '부과기관장', '유료도로여부']]
    df_refer = df_refer.astype(object).where(pd.notnull(df),None)
    refer_text = []
    for k, v in df_refer.iterrows() :
        cnt = 0
        for vv in v[1:] :
            if vv is not None :
                cnt +=1
        if cnt == 0 :
            refer_text.append(v[0])

    refer_text_total = '\n'.join(refer_text)

    return [official_adds, office_in_charge_f, car_reg_num, elec_invoice, violated_date, due_date, taxation_number, due_amount, violated_place, violated_content, taxation_officer, refer_text_total]


with open(r'rsc\templates_rawData.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total_dict = {}
# for image_file in glob.glob(r'rsc\templates\*.jpg') :
#     # print(Path(image_file).stem)
#     result_set = main_process(image_file, data)
#     total_dict[Path(image_file).stem] = result_set

# 개별 테스트용
image_file = r'rsc\templates\경상남도_진주시_교통행정과_168머6626_20210820184600.jpg'
main_process(image_file, data)


# df_final = pd.DataFrame(total_dict.values(), index = total_dict.keys(), columns = ['official_adds', 'office_in_charge', 'car_reg_num', 'elec_invoice', 'violated_date', 'due_date', 'taxation_number', 'due_amount', 'violated_place', 'violated_content', 'taxation_officer', 'refer_text_total'])
# df_final.to_excel(r'output\final.xlsx')





