import requests
import uuid
import time
import json, re, glob
from pathlib import Path

image_file = r'rsc\templates\서울문산고속도로_391마3219_20210707121619.jpg'
img_key = Path(image_file).stem

with open(r'output\fineTemplate.json', 'r', encoding='utf-8') as f :
    data = json.load(f)

print(data[img_key])

for txt in data[img_key] :
    date1 = re.compile(r'\d{4}-\d{1,2}-\d{1,2}\d{2}:\d{2}:\d{2}')
    date2 = re.compile(r'\d{4}년\d{1,2}월\d{1,2}일\d{2}시\d{2}분')
    date3 = re.compile(r'\d{4}-\d{1,2}-\d{1,2}\d{1,2}:\d{1,2}')
    date4 = re.compile(r'\d{4}.\d{1,2}.\d{1,2}\d{2}:\d{2}')

    electric_invoice1 = re.compile(r'\d+')
    electric_invoice2 = re.compile('(\d{5}-\d{1}-\d{2}-\d{2}-\d{9})')

    amt1 = re.compile(r'(\d{1,3},?\d{3}원)')
    amt2 = re.compile(r'(\d{1,3},?\d{3})')
    amt3 = re.compile(r'금액\d{1,3},?\d{3}')

    m1 = date1.search(txt)
    m2 = date2.search(txt)
    m3 = date3.search(txt)
    m4 = date4.search(txt)
    v1 = electric_invoice1.search(txt)
    v2 = electric_invoice2.search(txt)
    a1 = amt1.search(txt)
    a2 = amt2.search(txt)

    electric_invoice = ''.join(re.findall(electric_invoice2, txt))
    if electric_invoice :
        print(electric_invoice)
    
    amount = ''.join(re.findall(amt1, txt))
    if amount :
        print(amount)
    
    amount = ''.join(re.findall(amt2, txt))

    amount = ''.join(re.findall(amt3, txt))
    if amount.endswith('00') :
        print(amount)

    if m1:
        print('Match found: ', m1.group())
    elif m2 :
        print('Match found: ', m2.group())
    elif m3 :
        print('Match found: ', m3.group())
    elif m4 :
        print('Match found: ', m4.group())
    
    elif v1 :
        if len(v1.group()) == 19 :
            print('전자납부번호 : ', v1.group())
    
    elif v2 :
        print('전자납부번호 : ', v2.group())
    
    elif a1 :
        print(a1)
        print('금액 : ', a1.group())

    elif a2 :
        print(a2)
        print('금액 : ', a2.group())


    # date_time = ''.join(re.findall(r'\d{4}-\d{1,2}-\d{1,2}\d{2}:\d{2}:\d{2}', txt))

    # print(date_time)
    else : continue




# secret_key = 'elFDaGx5dm5SSWhjYnREQWFvSUJ6ckFxWXJ6dWJhWGg='
# api_url ='https://29280af484d34729ada88dcd3bbbfe3a.apigw.ntruss.com/custom/v1/6541/9f24228aa50496e90ee3a097e0fd65f27057b9a66468c1c7b5de681d2a39f137/general'

# request_json = {
#     'images': [
#         {
#             'format': 'jpg',
#             'name': 'demo'
#         }
#     ],
#     'requestId': str(uuid.uuid4()),
#     'version': 'V2',
#     'timestamp': int(round(time.time() * 1000))
# }

# payload = {'message': json.dumps(request_json).encode('UTF-8')}
# files = [
# ('file', open(image_file,'rb'))
# ]
# headers = {
# 'X-OCR-SECRET': secret_key
#   }

# response = requests.request("POST", api_url, headers=headers, data = payload, files = files)
# data = response.json()

# for i, item in enumerate(data['images'][0]['fields']) :
#     infer_text = item['inferText'].replace(" ", '')
#     print(infer_text)

