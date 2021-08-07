import pandas as pd
import os, glob
from pathlib import Path


df = pd.read_csv(r'C:\Users\C07037\Python_project\monthly_pqr\rsc\202107\TR2_20210802.csv', delimiter = '\t', low_memory=False)

previous_month = '20210630'  # 직전월
basis_month = '20210731'  # 기준월

with open(r'C:\Users\C07037\Python_project\monthly_pqr\src\constants.json', 'r', encoding='utf-8') as f :
    json_data = json.load(f)

default_paths = []
for k, v in json_data['folder'].items() :
    default_paths.append(v)

upper_dir = os.path.dirname(os.getcwd())

############ 기존 원본 정보 가져오기  #######  (latest folder)

# CB등급자료 가져오기
cb_grade_opening_latest_df = pd.read_pickle(os.path.join(r'C:\Users\C07037\Python_project\monthly_pqr\data\latest\cb_grade_opening_{}.pkl'.format(previous_month)))

# 조기상환, 리스승계 정보 가져오기
pre_payment_latest_df = pd.read_pickle(os.path.join(r'C:\Users\C07037\Python_project\monthly_pqr\data\latest\pre_payment_{}.pkl'.format(previous_month)))
                                
lease_transfer_latest_df = pd.read_pickle(os.path.join(r'C:\Users\C07037\Python_project\monthly_pqr\data\latest\lease_transfer_{}.pkl'.format(previous_month)))

# 일간 연체현황(HIstory) 자료 불러오기
daily_dlqt_latest_df = pd.read_pickle(os.path.join(r'C:\Users\C07037\Python_project\monthly_pqr\data\latest\daily_delqt_{}.pkl'.format(previous_month)))

# 여신잔액 자료(History) 불러오기
monthly_outstanding_latest_df = pd.read_pickle(os.path.join(r'C:\Users\C07037\Python_project\monthly_pqr\data\latest\monthly_outstanding_{}.pkl'.format(previous_month)))


read_dir = os.listdir(r'C:\Users\C07037\Python_project\monthly_pqr\rsc')
for x in read_dir :
    if x == basis_month[0:6] :
        read_files = glob.glob(r'C:\Users\C07037\Python_project\monthly_pqr\rsc' + x + '/*.*')
read_files = glob.glob(r'C:\Users\C07037\Python_project\monthly_pqr\rsc\202107'+ '/*.csv')


for a in read_files :
    if Path(a).stem.startswith('TR2_') :
        ledge_path = a
    elif Path(a).stem.startswith('TR99129') :
        cb_grade = a
    elif Path(a).stem.startswith('TR2008') :
        transfer = a
    elif Path(a).stem.startswith('TR2608') :
        pre_pay = a
    elif Path(a).stem.startswith('TR3741') :
        daily_dlqt = a


########## 해당월 데이터 가져오기 ###########

#  해당월 여신원장(마스터 정보) 불러오기
loan_outstandings_this_df = pd.read_csv(ledge_path, delimiter = '\t', low_memory=False)

# # 당해월 CB등급자료 가져오기
cb_grade_opening_this_df = pd.read_csv(cb_grade, delimiter = '\t')

# # 당해월 조기상환, 리스승계 정보 가져오기
pre_payment_this_df =  pd.read_csv(pre_pay, delimiter = '\t')

# 당해월 일간 연체현황(HIstory) 자료 불러오기
daily_dlqt_this_df =  pd.read_csv(pre_pay, delimiter = '\t')


quick_snap = df.groupby(['상품명'])['여신잔액'].sum()/1000000


# In[29]:


quick_snap.values


# In[15]:


# csv headers
TR2608 = ['관리부서', '거래처명', '실행번호', '실행일', '처리일', '물건처리', '상환구분', '승인상태', '선수금',
       '실제입금액', '상환전잔액', '상환원금', '중도상환수수료', '규손금', '보증금', '장기선수금', '차량번호',
       '물건명', '상품명', '회계구분']
TR2100 = ['No', '심의의결기구', '개최년도', '차수', '세부안건번호', '안건명', '거래상대방', '신규여부', '서면여부',
       '주요자산형태', '통화', '부의금액', '심의결과', '승인금액', '담당부팀점', '개최일자', '심의완료일자',
       '승인유효일자', '품의여부"', '품의일자', '실행일자', '대출금액', '여신잔액', '투자잔액(취득)',
       '투자잔액(평가)', '잔고수량', '품의번호', '실행번호', '실행상태', '상품코드', '상품명', '고객코드',
       '고객명', '원금상환형태', '한도여신여부', '계약금액', '한도잔액', '만기일', '한도계약만기일', '마감일자',
       '마감구분', '대출기간/투자기간', '변동금리여부"', '기본금리', '가산금리', '기초자산명', '발행회사',
       '업무집행조합원(GP)', '운용사', '종목코드(ISIN)', '종목명(한글)', '투자조합법적유형', '회사채등급고객',
       '어음등급고객', '기업등급고객', '신용공여1_고객번호', '신용공여1_고객명 신용공여1_사업지위', '신용공여1_형태',
       '신용공여1_세부형태', '신용공여1_약정미이행효과', '신용공여1_회사채등급', '신용공여2_고객번호', '신용공여2_고객명',
       '신용공여2_사업지위', '신용공여2_형태', '신용공여2_세부형태', '신용공여2_약정미이행효과', '신용공여2_회사채등급']
TR2008 = ['회계그룹', '부서', '품의번호', '공동계약', '품의상태', '고객명', '전결권자', '품의사유', '상품명',
       '품의일자', '승인일자', '여신금액', '리스료', '여신기간', '고객이자율', 'IRR', '여신시작일', '여신종료일',
       '보증금', '무보증잔가', '보증잔가', '원금유예금액', '공급자명', '종료후처리', '회계처리구분']


# In[ ]:





# In[ ]:


df1 = pd.read_csv(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2824_0630.csv', delimiter = '\t')


# In[ ]:


filtering_cols = ['부서', '상품명', '실행번호', '실행상태', '고객구분', '고객명', '고객번호', '담당자', '실행일자', '실행사유', '여신금액', '여신잔액', 
                  '여신시작일', '여신만기일', '여신기간', '리스\n계약회차','고객이자율', 'IRR', '차량가격', '보증금', '보증보험금액',
                  '무보증잔가', '보증잔가', '원금유예금액', '선수금', '장기선수금', '납부방법', '표준산업분류코드', '차량코드',
                  '제조사', '시리즈', '물건명', '차량번호', '차대번호', '유종', '잔가보장업체','잔가업체보장금액', '초과잔가율\n(%)', '프로모션\n(%)', '감가면제여부\n(YN)', 
                  '이전실행번호', '최초실행번호', '해지일자', '마감일자', '마감사유', '해지사유','월리스료', '승계수수료', '해지기한구분', '약정방식', '전자약정\n결과확인']


# In[ ]:


df_loan_ledge_pre_analysis = pd.merge(df_merged, df_loan_ledge_refined, how = 'left', left_on = '실행번호', right_on = '실행번호')


# In[ ]:


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


# 리테일 주요 상품
main_product = ['신차운용리스', '신차금융리스', '신차할부금융', '오토론신차대출', '스마트스토어대출', '스탁론(국내)', '임차보증금대출' ]
# 리테일 sub 상품
sub_product = ['오토론중고차대출', '바이크운용리스', '스탁론(해외)', '생명연계대출', '미트론', '주식담보대출' ,'NPL대출']
# 오토리스 분석제외 기업(도이치, 쏘카, SK네트웍스, 딜러사 금융 등)
exception_company = [1008109, 1000518, 1003192, 1029989, 1001717, 1003580]


# In[ ]:


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


# In[ ]:


# 통계위한 월말 기준 연체잔액 마스터 자료 (monthly_outstanding 컬럼 축소)
import copy

monthly_outstanding = monthly_outstanding[~monthly_outstanding['고객코드'].isin(exception_company)]
monthly_outstanding['상품분류'] = monthly_outstanding['상품명'].apply(product_cat)
selected_cols = ['실행번호', '고객코드', '부서', '상품명', '기준월', '상품분류', '여신금액', '여신잔액_x', '고객구분', '표준산업분류코드', '실행일자_y', '보증금', '장기선수금', '차량가격', '초과잔가율\n(%)', '무보증잔가', '고객이자율', 'IRR', '여신만기일', '개인신용\n평점구간']
monthly_outstanding_short = copy.deepcopy(monthly_outstanding[selected_cols])
monthly_outstanding_short['본인부담율'] = (monthly_outstanding_short['보증금'] + monthly_outstanding_short['장기선수금']) / monthly_outstanding_short['차량가격']
# monthly_outstanding_short.dropna(subset = ['실행번호'])
monthly_outstanding_short['기준월'] = monthly_outstanding_short['기준월'].apply(int)


# In[ ]:


def month_mod(num) :
    if num > 10000 :
        return str(num)
    else :
        return str(num+200000)

monthly_outstanding_short['기준월'] = monthly_outstanding_short['기준월'].apply(month_mod)


# In[ ]:





# In[ ]:




