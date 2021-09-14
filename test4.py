import requests
import uuid
import time
import json, re, glob
from pathlib import Path

def get_text(img) :
  secret_key = 'elFDaGx5dm5SSWhjYnREQWFvSUJ6ckFxWXJ6dWJhWGg='
  api_url ='https://29280af484d34729ada88dcd3bbbfe3a.apigw.ntruss.com/custom/v1/6541/9f24228aa50496e90ee3a097e0fd65f27057b9a66468c1c7b5de681d2a39f137/general'

  # image_file = r'rsc\경기도_안양시_만안구_교통녹지과_278소5733_20210827145100.jpg'

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
    ('file', open(img,'rb'))
  ]
  headers = {
    'X-OCR-SECRET': secret_key
  }

  response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

  return response.json()

total_data = {}

for fn in glob.glob(r'C:\Users\perkw\Projects\mis_project\rsc\templates\*.jpg') :
  data = get_text(fn)
  idx = Path(fn).stem

  dict_text = []
  cnt = 0
  for i, item in enumerate(data['images'][0]['fields']) :
    infer_text = item['inferText'].replace(" ", '')
    
    if (i > 0 and len(infer_text) == 1) or (i > 0 and len(infer_text) == 2 and infer_text.endswith((':', '/'))) or (i > 0 and ((re.match('\d{2}월', infer_text)) or (re.match('\d{2}일', infer_text)))) or (i > 0 and re.match('[^a-zA-Z가-힣]', infer_text)) :
    # if (i > 0 and len(infer_text) == 1) or (i > 0 and len(infer_text) == 2 and infer_text.endswith((':', '/'))) or (i > 0 and ((re.match('\d{2}월', infer_text)) or (re.match('\d{2}일', infer_text)))) :
      infer_text1 = dict_text[-1] + infer_text
      dict_text[i-1-cnt] = infer_text1
      cnt += 1
    else :
      dict_text.append(item['inferText'].replace(" ", ''))
  
  total_data[idx] = dict_text

  # for j, txt in enumerate(dict_text) :
  #   reg_dueDate = re.match(r'\d{4}년\d{2}월\d{2}일', txt)
  #   if '전자납부번호' in txt :
  #     print(txt)
  #     if re.match(r'\d{4}년\d{2}월\d{2}일', txt) :
  #       print(''.join(re.findall(r'\d{4}년\d{2}월\d{2}일', txt)))

with open(r'output/fineTemplate.json', 'w', encoding = 'utf-8') as f :
  json.dump(total_data, f,  indent=4)

print("done!")