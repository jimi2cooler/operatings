#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os


# In[5]:


print(os.getcwd())


# In[2]:


path = r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\여신잔액_tot_20210531.pkl'
df = pd.read_pickle(path)


# In[3]:


df.info()


# In[4]:


df1 = pd.read_excel(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2824_20210630_0.xlsx')


# In[5]:


df1['기준월'] = '202106'


# In[6]:


df2 = df1[['실행번호', '고객코드', '실행일자', '여신잔액', '기준월']]


# In[7]:


import datetime

df2.loc[:, '실행일자'] = df2.loc[:, '실행일자'].apply(lambda x : datetime.datetime.strptime(x, "%Y/%m/%d").strftime('%Y-%m-%d'))

# df['실행일자'] = df['실행일자'].apply(lambda x : datetime.datetime.strptime(x, '%Y%m%d'))
                                        
# df['실행일자'] = pd.to_datetime(df['실행일자'].astype(str), format='%Y%m%d')


# In[12]:


df2['여신잔액'] = df2['여신잔액'].apply(lambda x : x.replace(",", ""))
df2['여신잔액'].apply(int)


# In[13]:


df_merged = pd.concat([df, df2], ignore_index = True)


# In[14]:


df_merged.info()


# In[15]:


df_merged['실행일자'] = pd.to_datetime(df_merged['실행일자'], format='%Y-%m-%d')
df_merged['여신잔액'] = df_merged['여신잔액'].apply(int)


# In[16]:


df_merged.info()


# In[17]:


df_merged['여신잔액'] = df_merged['여신잔액'].apply(lambda col:pd.to_numeric(col, errors='coerce'))
df_merged['여신잔액'] = df_merged['여신잔액'].apply(lambda x : 0 if x < 0 else x)


# In[19]:


df_loan_ledge = pd.read_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2_20210705_0.pkl')


# In[57]:


# df_loan_ledge_1 = pd.read_excel(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\TR2818_20210630_0.xlsx')


# In[20]:


filtering_cols = ['부서', '상품명', '실행번호', '실행상태', '고객구분', '고객명', '고객번호', '담당자', '실행일자', '실행사유', '여신금액', '여신잔액', 
                  '여신시작일', '여신만기일', '여신기간', '리스\n계약회차','고객이자율', 'IRR', '차량가격', '보증금', '보증보험금액',
                  '무보증잔가', '보증잔가', '원금유예금액', '선수금', '장기선수금', '납부방법', '표준산업분류코드', '차량코드',
                  '제조사', '시리즈', '물건명', '차량번호', '차대번호', '유종', '잔가보장업체','잔가업체보장금액', '초과잔가율\n(%)', '프로모션\n(%)', '감가면제여부\n(YN)', 
                  '이전실행번호', '최초실행번호', '해지일자', '마감일자', '마감사유', '해지사유','월리스료', '승계수수료', '해지기한구분', '약정방식', '전자약정\n결과확인']


# In[66]:


# df_loan_ledge_1.columns [80:]


# In[21]:


df_loan_ledge_refined = df_loan_ledge[filtering_cols]


# In[22]:


df_loan_ledge_pre_analysis = pd.merge(df_merged, df_loan_ledge_refined, how = 'left', left_on = '실행번호', right_on = '실행번호')


# In[23]:


df_loan_ledge_pre_analysis.info()


# In[73]:


df_loan_ledge_pre_analysis.drop(['여신잔액_y'], axis=1, inplace=True)


# In[75]:


df_loan_ledge_pre_analysis = df_loan_ledge_pre_analysis.sort_values(['기준월', '실행번호'], ascending = [True, True])


# In[24]:


df_loan_ledge_pre_analysis.tail(20)


# In[25]:


df_loan_ledge_pre_analysis.to_pickle(r'C:\Users\C07037\Python_project\dlqt_analysis\rsc\dlqt_pre_analysis.pkl')

