#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from datetime import date,datetime


# In[ ]:


path = r'C:\Users\C07037\Python_project\dlqt_analysis\output'
# loan_outstandings = pd.read_excel(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2_20210705_0.xlsx')


# In[ ]:


#loan_outstandings.to_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2_20210705_0.pkl')


# In[ ]:


# temp : 엑셀 읽어서 pickle에 저장

cb_grade_opening = pd.read_excel(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\신용평점구간_20210630기준.xlsx')
cb_grade_opening.to_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\cb_grade_opening.pkl')

pre_payment_df = pd.read_excel(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2608_중도상환_20210708_00.xlsx')
pre_payment_df.to_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\pre_payment.pkl')

lease_transfer_df = pd.read_excel(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2008_승계품의등록_20210708_00.xlsx')
lease_transfer_df.to_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\lease_transfer.pkl')

# loan_outstandings_1 = pd.read_excel(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2818_20210630_0.xlsx')


# In[ ]:


lease_transfer_df.info()


# In[2]:


### pickle 자료 불러오기

# CB등급자료 가져오기
cb_grade_opening = pd.read_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\cb_grade_opening.pkl')

# 조기상환, 리스승계 정보 가져오기
pre_payment_df = pd.read_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\pre_payment.pkl')
lease_transfer_df = pd.read_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\lease_transfer.pkl')

# 여신현황 및 잔액 자료(History) 불러오기
monthly_outstanding_temp = pd.read_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\dlqt_pre_analysis.pkl')
monthly_outstanding_temp.dropna(subset = ['고객코드'], inplace = True)
monthly_outstanding_temp = monthly_outstanding_temp[~monthly_outstanding_temp['고객코드'].isna()]
monthly_outstanding = pd.merge(monthly_outstanding_temp, cb_grade_opening, how='left', left_on = '실행번호', right_on = '실행번호')
monthly_outstanding['실행월'] = monthly_outstanding['실행일자_y'].dt.strftime('%Y%m')

# 일간 연체현황(HIstory) 자료 불러오기
daily_dlqt_temp = pd.read_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\daily_delqt.pkl')
daily_dlqt = pd.merge(daily_dlqt_temp, cb_grade_opening, how='left', left_on = 'EXCFLDNBR', right_on = '실행번호')

# 여신원장(마스터 정보) 불러오기
loan_outstandings_temp = pd.read_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2_20210705_0.pkl')
loan_outstandings_temp1 = pd.merge(loan_outstandings_temp, cb_grade_opening, how='left', left_on = '실행번호', right_on = '실행번호')
loan_outstandings_temp1['품의번호'] = loan_outstandings_temp1['실행번호'].apply(lambda x: x[0:11])
lease_transfer_short = lease_transfer_df[['품의번호', '여신금액']]
loan_outstandings = pd.merge(loan_outstandings_temp1, lease_transfer_short, how='left', left_on = '품의번호', right_on = '품의번호')
loan_outstandings['실행월'] = loan_outstandings['실행일자'].dt.strftime('%Y%m')


# In[ ]:


monthly_outstanding_temp.info()


# In[3]:


# 리테일 주요 상품
main_product = ['신차운용리스', '신차금융리스', '신차할부금융', '오토론신차대출', '스마트스토어대출', '스탁론(국내)', '임차보증금대출' ]
# 리테일 sub 상품
sub_product = ['오토론중고차대출', '바이크운용리스', '스탁론(해외)', '생명연계대출', '미트론', '주식담보대출' ,'NPL대출']
# 오토리스 분석제외 기업(도이치, 쏘카, SK네트웍스, 딜러사 금융 등)
exception_company = [1008109, 1000518, 1003192, 1029989, 1001717, 1003580]


# In[4]:


def product_cat(product) :
    if product in main_product :
        if product in ['신차운용리스'] : 
            return '오토리스'
        elif product in ['신차금융리스', '신차할부금융', '오토론신차대출'] :
            return '할부/오토론'
        elif product in ['스마트스토어대출', '스탁론(국내)', '임차보증금대출'] :
            return product
        else :
            return product
    else :
        if product in ['오토론중고차대출', '바이크운용리스'] :
            return '오토_기타'
        elif product in ['스탁론(해외)', '생명연계대출', '미트론', '주식담보대출' ,'NPL대출'] :
            return "데이터_기타"
        else : 
            return '기타'


# In[5]:


# 통계위한 월말 기준 연체잔액 마스터 자료 (monthly_outstanding 컬럼 축소)
import copy

monthly_outstanding = monthly_outstanding[~monthly_outstanding['고객코드'].isin(exception_company)]
monthly_outstanding['상품분류'] = monthly_outstanding['상품명'].apply(product_cat)
selected_cols = ['실행번호', '고객코드', '부서', '상품명', '기준월', '상품분류', '여신금액', '여신잔액_x', '고객구분', '표준산업분류코드', '실행일자_y', '보증금', '장기선수금', '차량가격', '초과잔가율\n(%)', '무보증잔가', '고객이자율', 'IRR', '여신만기일', '개인신용\n평점구간']
monthly_outstanding_short = copy.deepcopy(monthly_outstanding[selected_cols])
monthly_outstanding_short['본인부담율'] = (monthly_outstanding_short['보증금'] + monthly_outstanding_short['장기선수금']) / monthly_outstanding_short['차량가격']
# monthly_outstanding_short.dropna(subset = ['실행번호'])
monthly_outstanding_short['기준월'] = monthly_outstanding_short['기준월'].apply(int)


# In[6]:


def month_mod(num) :
    if num > 10000 :
        return str(num)
    else :
        return str(num+200000)

monthly_outstanding_short['기준월'] = monthly_outstanding_short['기준월'].apply(month_mod)


# In[7]:


daily_dlqt['LN_DLY_AMT'] = daily_dlqt['DLYLESAMT'] + daily_dlqt['CLNINTAMT']
daily_dlqt['LN_DLY_AMT'] = pd.to_numeric(daily_dlqt['LN_DLY_AMT'])


# In[8]:


daily_dlqt = daily_dlqt[daily_dlqt['SCHFLDKND'] == 'FI670001']
daily_dlqt = daily_dlqt[daily_dlqt['LN_DLY_AMT'] > 0]


# In[9]:


# 날짜형식 데이터 Date 형식으로 변환
daily_dlqt['DLYSTADAT'] =   pd.to_datetime(daily_dlqt['DLYSTADAT'].astype(str), format='%Y-%m-%d') 
daily_dlqt['PMTAFTDAT'] =   pd.to_datetime(daily_dlqt['PMTAFTDAT'].astype(str), format='%Y-%m-%d') 
daily_dlqt['ACPPMTDAT'] =   pd.to_datetime(daily_dlqt['ACPPMTDAT'].astype(str), format='%Y-%m-%d')

# 실납부일과 기준일자 사이의 날짜 구하기
daily_dlqt['ACT_DLQT_DAY'] = (daily_dlqt['DLYSTADAT']-daily_dlqt['ACPPMTDAT']).dt.days

# index 지우기 
# daily_dlqt.drop(['index'], axis=1, inplace=True)

# 정렬하기
daily_dlqt = daily_dlqt.sort_values(['EXCFLDNBR', 'DLYSTADAT', 'RFDFLDODR'], ascending = [True, True, False])


# In[ ]:


daily_dlqt.info()


# In[ ]:


* 마스터성(최근 조회기준일자 기준) 자료 Grouping
    - A : 실행번호별 1일,3일, 5일, 10일, 15일, 20일, 30일, 60일, 90일 연체 최초 발생일자, 발생월
    - B : 실행번호별 1일,3일, 5일, 10일, 15일, 20일, 30일, 60일, 90일 연체 최초 발생회차(원리금스케줄)
    - C : 실행번호별 연체경험횟수
    - D : 실행번호별 최대연체일수
    - E : 실행번호별 회차별 연체평균일수(연체해제평균일자)
    
* 시계열(월말 기준) 자료
  - F : 월말별 실행번호별 5일, 10일, 20일, 30일, 60일, 90일 이상 건수, 연체원리금


# In[10]:


# 연체일수 Label 함수

def dlqt_class(day) : 
    if day < 5 :
        return 'U5'
    elif 5<= day < 10 :
        return '5D'
    elif 10 <= day < 15 :
        return '10D'
    elif 15 <= day < 20 :
        return '15D'
    elif 20 <= day < 30 :
        return '20D'
    elif 30 <= day < 60 :
        return '30D'
    elif 60 <= day < 90 :
        return '60D'
    else :
        return '90D'


# In[11]:


daily_dlqt['DLQT_CLASS'] = daily_dlqt['ACT_DLQT_DAY'].apply(lambda x : dlqt_class(x))


# In[12]:


# 연체일수 Threshold Hit 기준 DataFrame 생성
import time

threshold_gb = [1, 3, 5, 10, 15, 20, 30, 60, 90]

threshold_hit_df = {}

for gb in threshold_gb :
    df = daily_dlqt[daily_dlqt['ACT_DLQT_DAY'] == gb].reset_index()
    df['HIT_THLD_YM'] = df['DLYSTADAT'].dt.strftime('%Y%m')
    threshold_hit_df['dlqt_%dD'% gb] = df   


# In[13]:


# 실행번호별 연체발생 함수(1~90일 최초 발생일자, 발생월 Dataframe 생성)
dlqt_exprience_dict = {}

for k, v in threshold_hit_df.items() :
    filtered_df = v.groupby(['EXCFLDNBR','DLYSTADAT'])['RFDFLDODR'].min().reset_index()
    filtered_df_temp = filtered_df.groupby(['EXCFLDNBR'])['DLYSTADAT'].min().reset_index()
    filtered_df_temp['HIT_THLD_YM'] = filtered_df_temp['DLYSTADAT'].dt.strftime('%Y%m')
    filtered_df_temp['HIT_YN'] = 1 # 경험여부가 Y일경우 1
    
    dlqt_exprience_dict['{}_experience_df'.format(k)] = filtered_df_temp


# In[14]:


# 연체일자별 월간 통계자료 작성 (월말 잔액DB와 연체경험 left joining)
dlqt_stat_dict = {}

for k, v in dlqt_exprience_dict.items() :
    join_df = pd.merge(monthly_outstanding_short, v, left_on=['실행번호','기준월'], right_on=['EXCFLDNBR','HIT_THLD_YM'], how='left')
    join_df['HIT_YN'] = join_df['HIT_YN'].fillna(0)
    dlqt_stat_dict['{}_stat'.format(k)] = join_df


# In[15]:


# 연체기준일별 월간 통계 DF로 cross tab 결과 도출 및 정렬

dlqt_stat_by_month_dic = {}

for k, v in dlqt_stat_dict.items() :
    cross_stat = pd.crosstab(v['기준월'], [v['상품분류'], v['HIT_YN']], margins = True)
    col_sort_list = ['오토리스', '할부/오토론', '임차보증금대출', '스탁론(국내)', '스마트스토어대출', '오토_기타', '데이터_기타', '기타']
    dlqt_stat_by_month_dic['{}_result'] = cross_stat[col_sort_list]


# In[ ]:


monthly_5d_hit = dlqt_stat_dict['dlqt_5D_experience_df_stat']

monthly_5d_hit_stat = pd.crosstab(monthly_5d_hit['기준월'], monthly_5d_hit['HIT_YN'], monthly_5d_hit['실행번호'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)


# In[ ]:


monthly_5d_hit_stat.values[:,1]


# In[ ]:


# 리테일상품 월별 신규 연체일별 발생비율 _ 전체

monthly_new_dlqt_by_duration_list = []

for gb in threshold_gb[0:7] :
    monthly_dlqt_hit_by_day = dlqt_stat_dict['dlqt_{}D_experience_df_stat'.format(gb)]
    monthly_dlqt_hit_by_day_stat = pd.crosstab(monthly_dlqt_hit_by_day['기준월'], monthly_dlqt_hit_by_day['HIT_YN'], monthly_dlqt_hit_by_day['실행번호'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)
    monthly_new_dlqt_by_duration_list.append(monthly_dlqt_hit_by_day_stat.values[:,1])

nparray = np.array(monthly_new_dlqt_by_duration_list)
monthly_new_dlqt_by_duration_index = monthly_dlqt_hit_by_day_stat.index

monthly_new_dlqt_by_duration_all = pd.DataFrame(data=nparray.T, index = monthly_new_dlqt_by_duration_index, columns=['1D', '3D', '5D', '10D', '15D', '20D', '30D'])


# In[ ]:


# 리테일상품 월별 신규 연체일별 발생비율 _ 오토

monthly_new_dlqt_by_duration_list = []
auto_select = ['오토리스', '할부/오토론']

for gb in threshold_gb[0:7] :
    monthly_dlqt_hit_by_day = dlqt_stat_dict['dlqt_{}D_experience_df_stat'.format(gb)]
    monthly_dlqt_hit_by_day = monthly_dlqt_hit_by_day[monthly_dlqt_hit_by_day['상품분류'].isin(auto_select)]
    monthly_dlqt_hit_by_day_stat = pd.crosstab(monthly_dlqt_hit_by_day['기준월'], monthly_dlqt_hit_by_day['HIT_YN'], monthly_dlqt_hit_by_day['실행번호'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)
    monthly_new_dlqt_by_duration_list.append(monthly_dlqt_hit_by_day_stat.values[:,1])

nparray = np.array(monthly_new_dlqt_by_duration_list)
monthly_new_dlqt_by_duration_index = monthly_dlqt_hit_by_day_stat.index

monthly_new_dlqt_by_duration_auto = pd.DataFrame(data=nparray.T, index = monthly_new_dlqt_by_duration_index, columns=['1D', '3D', '5D', '10D', '15D', '20D', '30D'])


# In[16]:


# 연체경험 일자별 시작회차 Dataframe 만들기

dlqt_experience_seq_dict = {}  # 연체경험 회차

for k, v in threshold_hit_df.items() :
    filtered_df = v.groupby(['EXCFLDNBR'])['RFDFLDODR'].min().reset_index()
    dlqt_experience_seq_dict['{}_experience_seq'.format(k)] = filtered_df 
    
# dlqt_1D_experience_seq_df = get_dlqt_start_seq(dlqt_1D)
# dlqt_3D_experience_seq_df = get_dlqt_start_seq(dlqt_3D)
# dlqt_5D_experience_seq_df = get_dlqt_start_seq(dlqt_5D)
# dlqt_10D_experience_seq_df = get_dlqt_start_seq(dlqt_10D)
# dlqt_15D_experience_seq_df = get_dlqt_start_seq(dlqt_15D)
# dlqt_20D_experience_seq_df = get_dlqt_start_seq(dlqt_20D)
# dlqt_30D_experience_seq_df = get_dlqt_start_seq(dlqt_30D)
# dlqt_60D_experience_seq_df = get_dlqt_start_seq(dlqt_60D)
# dlqt_90D_experience_seq_df = get_dlqt_start_seq(dlqt_90D)


# In[17]:


dlqt_experience_seq_dict['dlqt_5D_experience_seq']


# In[ ]:


#실행번호별 연체경험 횟수
# 1. 연체 1일 경험횟수 (회차별 연체 1일 이상인 회차의 갯수)
dlqt_1D_experience_times_temp = threshold_hit_df['dlqt_1D'].groupby(['EXCFLDNBR','RFDFLDODR'])['ACT_DLQT_DAY'].count().reset_index()
dlqt_1D_experience_times_df = dlqt_1D_experience_times_temp.groupby(['EXCFLDNBR'])['RFDFLDODR'].count().reset_index()

# 2. 연체 3일 경험횟수 (회차별 연체 3일 경험 회차의 갯수)
dlqt_3D_experience_times_temp = threshold_hit_df['dlqt_3D'].groupby(['EXCFLDNBR','RFDFLDODR'])['ACT_DLQT_DAY'].count().reset_index()
dlqt_3D_experience_times_df = dlqt_3D_experience_times_temp.groupby(['EXCFLDNBR'])['RFDFLDODR'].count().reset_index()

# 3. 연체 5일 경험횟수 (회차별 연체 5일 경험 회차의 갯수)
dlqt_5D_experience_times_temp = threshold_hit_df['dlqt_5D'].groupby(['EXCFLDNBR','RFDFLDODR'])['ACT_DLQT_DAY'].count().reset_index()
dlqt_5D_experience_times_df = dlqt_5D_experience_times_temp.groupby(['EXCFLDNBR'])['RFDFLDODR'].count().reset_index()


# In[68]:


dlqt_transition_df.info()


# In[ ]:


# 실행번호별 최대연체일수

dlqt_experience_max_days = daily_dlqt.groupby(['EXCFLDNBR'])['ACT_DLQT_DAY'].max().reset_index()


# In[ ]:


# 실행번호별 평균연체일수

dlqt_experience_average_days_temp = daily_dlqt.groupby(['EXCFLDNBR', 'RFDFLDODR'])['ACT_DLQT_DAY'].max().reset_index()
dlqt_experience_average_days = dlqt_experience_average_days_temp.groupby(['EXCFLDNBR'])['ACT_DLQT_DAY'].mean().reset_index()


# In[18]:


# 기준일자가 월말인 DataFrame 필터링
monthly_dlqt = daily_dlqt[daily_dlqt['DLYSTADAT'].dt.is_month_end].reset_index()
# index 컬럼 지우기
monthly_dlqt.drop(['index'], axis=1, inplace=True)


# In[19]:


# 기준월 Label 작업
monthly_dlqt['MONTH_BASIS'] = monthly_dlqt['DLYSTADAT'].dt.strftime('%Y%m')


# In[44]:


# 누적 연체원금, 연체이자, 연체기타, Count
monthly_dlqt = monthly_dlqt.sort_values(['EXCFLDNBR', 'DLYSTADAT', 'RFDFLDODR'], ascending = [True, True, False])
monthly_dlqt['CUM_PRINCIPAL_DLQT'] = monthly_dlqt.groupby(by=['EXCFLDNBR', 'DLYSTADAT'])['DLYPRNAMT'].transform(lambda x: x.cumsum())
monthly_dlqt['CUM_INTEREST_DLQT'] = monthly_dlqt.groupby(by=['EXCFLDNBR', 'DLYSTADAT'])['DLYINTAMT'].transform(lambda x: x.cumsum())
monthly_dlqt['CUM_ETC_DLQT'] = monthly_dlqt.groupby(by=['EXCFLDNBR', 'DLYSTADAT'])['DLYETCAMT'].transform(lambda x: x.cumsum())
monthly_dlqt['CUM_COUNT'] = monthly_dlqt.groupby(by=['EXCFLDNBR', 'DLYSTADAT']).cumcount()+1


# In[50]:


# 월별 연체회차 순번이 Max인 Master 자료 구하기

monthly_dlqt_max_seq = monthly_dlqt.groupby(['EXCFLDNBR', 'DLYSTADAT'])['CUM_COUNT'].max().reset_index()
monthly_dlqt_master = pd.merge(monthly_dlqt, monthly_dlqt_max_seq, on = ['EXCFLDNBR', 'DLYSTADAT', 'CUM_COUNT'])


# In[53]:


# 연체전이율 분석

dlqt_transition_df = pd.merge(monthly_outstanding_short, monthly_dlqt_master, how = 'left', left_on=['실행번호', '기준월'], right_on=['EXCFLDNBR', 'MONTH_BASIS']).reset_index()


# In[57]:


# 정상인 경우 0 회차로 만들기
dlqt_transition_df['CUM_COUNT'].fillna(value=0, inplace=True)


# In[59]:


# 월별 List 만들기
month_list = dlqt_transition_df['기준월'].unique()


# In[65]:


# 분석기간 월 Label 가져오기 (즉, 최근 6개월이면 마지막으로부터 7개 가져오기)
window_month_list = month_list[-7:]


# In[70]:


previous_month_dlqt = dlqt_transition_df[dlqt_transition_df['기준월'] == '202012']
current_month_dlqt = dlqt_transition_df[dlqt_transition_df['기준월'] == '202101']


# In[77]:


previous_month_dlqt_crosstab = previous_month_dlqt[['실행번호_x', 'CUM_COUNT',  '여신잔액_x']]
current_month_dlqt_crosstab = current_month_dlqt[['실행번호_x', 'CUM_COUNT', '여신잔액_x']]


# In[78]:


previous_month_dlqt_crosstab.info()


# In[80]:


dlqt_transition_master = pd.merge(previous_month_dlqt_crosstab, current_month_dlqt_crosstab, on = '실행번호_x', how='left')


# In[83]:


dlqt_transition_master['CNT'] = 1


# In[84]:


cross_result = pd.crosstab(dlqt_transition_master['CUM_COUNT_x'], dlqt_transition_master['CUM_COUNT_y'], dlqt_transition_master['CNT'], aggfunc='count')


# In[85]:


cross_result


# In[69]:


# 전월과 당월 pair  만들기
monthly_dlqt_transition_dict = {}

for i, month in enumerate(window_month_list) :
    if i < len(window_month_list)-1 :
        previous_month = month
        current_month = window_month_list[i+1]
        
        previous_month_dlqt = dlqt_transition_df[dlqt_transition_df['기준월'] == previous_month]
        current_month_dlqt = dlqt_transition_df[dlqt_transition_df['기준월'] == current_month]
        previous_month_dlqt['CNT_VIRTUAL'] = 1
        current_month_dlqt['CNT_VIRTUAL'] = 1
        
        previous_month_dlqt_crosstab = previous_month_dlqt[['EXCFLDNBR', 'CUM_COUNT', 'CNT_VIRTUAL', '여신잔액_x']]
        current_month_dlqt_crosstab = current_month_dlqt[['EXCFLDNBR', 'CUM_COUNT', 'CNT_VIRTUAL', '여신잔액_x']]
        
        dlqt_transition_master = pd.merge(previous_month_dlqt_crosstab, current_month_dlqt_crosstab, on = 'EXCFLDNBR', how='left')
        cross_result = pd.crosstab(dlqt_transition_master['CUM_COUNT_x'], dlqt_transition_master['CUM_COUNT_y'], aggfunc='count')
        
        monthly_dlqt_transition_dict[current_month] = cross_result
        
    else :
        break


# In[ ]:


# 월간 상품별 잔고 추이
filter_org = ['데이터금융1팀', '리스할부운영팀', '리스할부영업팀','데이터금융2팀', '데이터금융3팀']  # 리테일조직명
monthly_outstanding_ready = monthly_outstanding_short[monthly_outstanding_short['부서'].isin(filter_org)]  # 리테일조직으로 필터링

monthly_loan_outstanding_by_product = pd.crosstab(monthly_outstanding_ready['기준월'], monthly_outstanding_ready['상품분류'], monthly_outstanding_ready['여신잔액_x']/1000000, aggfunc='sum')
col_sort_list = ['오토리스', '할부/오토론', '임차보증금대출', '스탁론(국내)', '스마트스토어대출', '오토_기타', '데이터_기타', '기타']
monthly_loan_outstanding_by_product = monthly_loan_outstanding_by_product[col_sort_list]


# In[ ]:


# 월간 상품별 고객수 추이
monthly_customer_count_by_product = pd.crosstab(monthly_outstanding_ready['기준월'], monthly_outstanding_ready['상품분류'], monthly_outstanding_ready['고객코드'], aggfunc='count')
col_sort_list = ['오토리스', '할부/오토론', '임차보증금대출', '스탁론(국내)', '스마트스토어대출']
monthly_lcustomer_count_by_product = monthly_customer_count_by_product[col_sort_list]


# In[ ]:


# 상품분류별 평균금리 구하기

mean_apr_by_product = pd.crosstab(monthly_outstanding_ready['기준월'], monthly_outstanding_ready['상품분류'], monthly_outstanding_ready['고객이자율'], aggfunc='mean')
mean_irr_by_product = pd.crosstab(monthly_outstanding_ready['기준월'], monthly_outstanding_ready['상품분류'], monthly_outstanding_ready['IRR'], aggfunc='mean')
col_sort_list = ['오토리스', '할부/오토론', '임차보증금대출', '스탁론(국내)', '스마트스토어대출']
mean_apr_by_product = mean_apr_by_product[col_sort_list]
mean_irr_by_product = mean_irr_by_product[col_sort_list]


# In[ ]:


# 고객구분별 비중추이 구하기

ratio_cumstomer_class = pd.crosstab(monthly_outstanding_ready['기준월'], monthly_outstanding_ready['고객구분'], monthly_outstanding_ready['실행번호'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)


# In[ ]:


monthly_outstanding_ready.info()


# In[ ]:


# 리스할부 고객구분별 비중, 신용등급 비중 추이 구하기
filter_cols = ['오토리스', '할부/오토론']
monthly_outstanding_ready_auto = monthly_outstanding_ready[monthly_outstanding_ready['상품분류'].isin(filter_cols)]
ratio_auto_cumstomer_class = pd.crosstab(monthly_outstanding_ready_auto['기준월'], monthly_outstanding_ready_auto['고객구분'], monthly_outstanding_ready_auto['고객코드'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)
ratio_auto_by_grade = pd.crosstab(monthly_outstanding_ready_auto['기준월'], monthly_outstanding_ready_auto['개인신용\n평점구간'], monthly_outstanding_ready_auto['고객코드'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)


# In[ ]:


ratio_auto_by_grade


# In[ ]:


# 데이터금융 고객구분별 비중, 신용등급 비중 추이 구하기
filter_cols_1 = ['스마트스토어대출', '스탁론(국내)', '임차보증금대출']
monthly_outstanding_ready_data = monthly_outstanding_ready[monthly_outstanding_ready['상품분류'].isin(filter_cols_1)]
ratio_data_division_cumstomer_class = pd.crosstab(monthly_outstanding_ready_data['기준월'], monthly_outstanding_ready_data['고객구분'], monthly_outstanding_ready_data['고객코드'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)
ratio_data_division_by_grade = pd.crosstab(monthly_outstanding_ready_data['기준월'], monthly_outstanding_ready_data['개인신용\n평점구간'], monthly_outstanding_ready_data['고객코드'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)


# In[ ]:


# 임대보증금 비중, 신용등급 비중 추이 구하기
filter_cols_2 = ['임차보증금대출']
monthly_outstanding_ready_apt = monthly_outstanding_ready[monthly_outstanding_ready['상품분류'].isin(filter_cols_2)]
# ratio_apt_lease_cumstomer_class = pd.crosstab(monthly_outstanding_ready_data['기준월'], monthly_outstanding_ready_data['고객구분'], monthly_outstanding_ready_data['고객코드'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)
ratio_apt_lease_by_grade = pd.crosstab(monthly_outstanding_ready_apt['기준월'], monthly_outstanding_ready_apt['개인신용\n평점구간'], monthly_outstanding_ready_apt['고객코드'], aggfunc='count').apply(lambda r: r/r.sum(), axis=1)


# In[ ]:


# 연체 5,30, 60, 90일 이상 채권의 신용등급 분포

dlqt_90d_df = threshold_hit_df['dlqt_90D']
grade_by_90d_dlqt = dlqt_90d_df.groupby(['개인신용\n평점구간'])['고객번호'].count()

dlqt_60d_df = threshold_hit_df['dlqt_60D']
grade_by_60d_dlqt = dlqt_60d_df.groupby(['개인신용\n평점구간'])['고객번호'].count()

dlqt_30d_df = threshold_hit_df['dlqt_30D']
grade_by_30d_dlqt = dlqt_30d_df.groupby(['개인신용\n평점구간'])['고객번호'].count()

dlqt_5d_df = threshold_hit_df['dlqt_5D']
grade_by_5d_dlqt = dlqt_5d_df.groupby(['개인신용\n평점구간'])['고객번호'].count()


# In[ ]:


# 중도상환 통계 (리테일 전체)

mapping_outstading = loan_outstandings[['실행번호', '고객번호_x']]

pre_payment_df['처리월'] =   pd.to_datetime(pre_payment_df['처리일'].astype(str), format='%Y-%m-%d')
pre_payment_df['처리월'] = pre_payment_df['처리월'].dt.strftime('%Y%m')
col_filter_prepay = ['신차운용리스', '신차금융리스', '신차할부금융', '오토론신차대출', '임차보증금대출', '스탁론(국내)', '스마트스토어대출']
pre_payment_df = pre_payment_df[pre_payment_df['상품명'].isin(col_filter_prepay)]

pre_payment_mapped = pd.merge(pre_payment_df, mapping_outstading, how='left', left_on = '실행번호', right_on = '실행번호')

pre_payment_mapped = pre_payment_mapped[~pre_payment_mapped['고객번호_x'].isin(exception_company)]

monthly_prepay_amount = pd.crosstab(pre_payment_mapped['처리월'], pre_payment_mapped['상환구분'], pre_payment_mapped['실제입금액']/1000000, aggfunc='sum')
monthly_prepay_count = pd.crosstab(pre_payment_mapped['처리월'], pre_payment_mapped['상환구분'], pre_payment_mapped['실행번호'], aggfunc='count')


# In[ ]:


# 중도상환 통계 (오토본부)

auto_filter = ['신차운용리스', '신차금융리스', '신차할부금융', '오토론신차대출']
pre_payment_mapped_auto = pre_payment_mapped[pre_payment_mapped['상품명'].isin(auto_filter)]

monthly_prepay_amount_auto = pd.crosstab(pre_payment_mapped_auto['처리월'], pre_payment_mapped_auto['상환구분'], pre_payment_mapped_auto['실제입금액']/1000000, aggfunc='sum')
monthly_prepay_count_auto = pd.crosstab(pre_payment_mapped_auto['처리월'], pre_payment_mapped_auto['상환구분'], pre_payment_mapped_auto['실행번호'], aggfunc='count')


# In[ ]:


monthly_prepay_amount_auto


# In[ ]:


# 승계관련 통계

lease_transfer_stat = loan_outstandings[loan_outstandings['실행사유'] == '이용자승계']
lease_transfer_stat = lease_transfer_stat[['실행번호', '고객구분', '고객번호_x', '실행월']]

monthly_lease_transfer_count = lease_transfer_stat.groupby(['실행월'])['실행번호'].count()


# In[ ]:


# 재리스 처리 건수

lease_transfer_resale = loan_outstandings[loan_outstandings['실행사유'] == '재리스']
lease_transfer_resale = lease_transfer_resale[['실행번호', '고객구분', '고객번호_x', '실행월']]

monthly_lease_resale_count = lease_transfer_resale.groupby(['실행월'])['실행번호'].count()


# In[ ]:


def brand_cat(brand) :
    if brand in main_car_brand :
        return brand
    else :
        return "etc. Brand"


# In[ ]:


# 잔가 추이
main_car_brand = ['MERCEDES BENZ', 'BMW', 'AUDI', 'PORSCHE']
rv_loan_outstanding = loan_outstandings[loan_outstandings['실행상태'] == '정상']
rv_loan_outstanding = loan_outstandings[loan_outstandings['상품명'] == '신차운용리스']
rv_loan_outstanding = loan_outstandings[loan_outstandings['여신만기일'].isin(pd.date_range('2021-07-01', '2026-07-01'))]

rv_loan_outstanding['만기월'] = rv_loan_outstanding['여신만기일'].dt.strftime('%Y%m')

rv_loan_outstanding['car_main_brand'] = rv_loan_outstanding['제조사'].apply(brand_cat)

rv_by_monthend = pd.crosstab(rv_loan_outstanding['만기월'], rv_loan_outstanding['car_main_brand'], rv_loan_outstanding['무보증잔가']/1000000, aggfunc='sum')
rv_by_monthend_acc = pd.crosstab(rv_loan_outstanding['만기월'], rv_loan_outstanding['car_main_brand'], rv_loan_outstanding['무보증잔가']/1000000, aggfunc='sum').transform(lambda x: x.cumsum())


# In[ ]:


rv_by_monthend_acc


# In[ ]:





# In[ ]:


### -> 이하 그림 그리기


# In[ ]:


import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns


# In[ ]:


plt.rcParams.update({'font.size': 10})
plt.rcParams.update({'font.family': 'Gulim'})


# In[ ]:


# [누적 Bar plot]

fig = plt.figure(figsize=(10, 5), dpi=200)
ax = plt.gca()
# 차트 제목
plt.title('할부리스 신규 연체일별 발생 비율 추이')
plt.xlabel('월')
plt.ylabel('비율')
file_name = '24. 할부리스 신규 연체일별 발생 비율 추이'
monthly_new_dlqt_by_duration_auto.plot(kind='line', ax=ax, stacked = False)
plt.show()
fig.savefig(r'C:\Users\C07037\Python_project\dlqt_analysis\output\{}.png'.format(file_name))


# In[ ]:


# 월별 리테일자산 여신잔액 비중 추이

monthly_loan_outstanding_ratio_by_product = pd.crosstab(monthly_outstanding_ready['기준월'], monthly_outstanding_ready['상품분류'], monthly_outstanding_ready['여신잔액_x']/1000000, aggfunc='sum').apply(lambda r: r/r.sum(), axis=1)
col_sort_list = ['오토리스', '할부/오토론', '임차보증금대출', '스탁론(국내)', '스마트스토어대출', '오토_기타', '데이터_기타', '기타']
monthly_loan_outstanding_ratio_by_product = monthly_loan_outstanding_ratio_by_product[col_sort_list]


# In[ ]:


monthly_loan_outstanding_ratio_by_product


# In[ ]:


col_sort_list = ['오토리스', '할부/오토론', '임차보증금대출', '스탁론(국내)', '스마트스토어대출']
monthly_loan_outstanding_ratio_by_product = monthly_loan_outstanding_ratio_by_product[col_sort_list]


# In[ ]:


monthly_loan_outstanding_ratio_by_product


# In[ ]:



fig = plt.figure(figsize=(10, 5), dpi=200)
ax = plt.gca()
# 차트 제목
plt.title('고객별 연체최대일수 분포')
plt.xlabel('연체일수')
plt.ylabel('빈도')
file_name = '21. 고객별 연체최대일수 분포'

list = []
for i in range(0, 30) :
    list.append(i)

plt.hist(dlqt_experience_max_days['ACT_DLQT_DAY'], list , density=True, color='blue', histtype='bar')
plt.show()
fig.savefig(r'C:\Users\C07037\Python_project\dlqt_analysis\output\{}.png'.format(file_name))


# In[ ]:


dlqt_experience_max_days['ACT_DLQT_DAY']


# In[ ]:




