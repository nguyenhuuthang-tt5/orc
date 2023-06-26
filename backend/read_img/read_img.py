import io
from google.cloud import vision
from google.cloud.vision_v1 import types
import os
import pathlib
import unidecode
import re
import pandas as pd
from datetime import date

def get_hospital_name(str_list: list, hos_dict: dict, res_string_list: list):
    result = ''
    length = 0
    for string in str_list:
        for k, v in hos_dict.items():
            if length <= len(str(string)) and 'BENH VIEN' in string:
                if string in k  or k in string:
                    result = v
                    length = len(string)
    return result

def get_patient_age(str_list:list,  res_string_list: list):
    regex = r'\b(Tuo?i?\w*|AGE|TUO?I?\w*)\s*\:?\s*\d+\b'
    # regex = r'\b(Na?m?\s*s?i?n?h?)\s*\:?\s*\d+\b'
    tuoi = -1
    for string in str_list:
        if(re.search(regex, string=string)):
            tuoi = [int(s) for s in string.split() if s.isdigit()][0]
    if tuoi == -1:
        for string in res_string_list:
            if(re.search(regex, string=string)):
                tuoi = [int(s) for s in string.split() if s.isdigit()][0]
    if tuoi >= 1000:
        today = date.today()
        tuoi = int(today.year) - tuoi
    return tuoi
            
def get_medicine(str_list: list, thuoc_df: pd.DataFrame, res_string_list: list):

    medicine_list = list()
    str_dict = dict(zip(res_string_list, str_list))
    active = list(thuoc_df['HOAT_CHAT'].apply(lambda x: r'\b(' + '|'.join([re.escape(x2) for x2 in str(x).split('+')]) + r')\d*(mg)*\b'))
    
    for k, v in str_dict.items():
        name = list(thuoc_df['TEN_THUOC'].apply(lambda x: re.search(pattern=r'\b' + x + r'\b', string=v, flags=re.IGNORECASE)).dropna())
        if len(name) > 0 :
            medicine_list.append(k)
        else:
            for reg in active:
                if re.search(reg, v, re.IGNORECASE):
                    medicine_list.append(k)
                    break
    return medicine_list

def get_gender(str_list: list, res_string_list: list):
    regex = r'\b(GIOI TINH|GENDER)\s*\:?\s*(NAM|NU|MALE|FEMALE)\b'
    regex2 = r'\bG?iới tính?\b|Nữ|Nam'
    gender = ''
    for string in str_list:
        if(re.search(regex, string=string)):
            gender = string.strip()
    if gender == '':
        for string in res_string_list:
            if re.search(regex2, string=string):
                gender = string
    return gender.strip()

def get_diagnose(para_list:list, res_para_list: list):

    dict1 = dict(zip(res_para_list, para_list))
    regex = r'\bCHAN DOA?N?\s*\:?\s*\w+\b'
    chandoan = ''
    
    for k, v in dict1.items():
        if(re.search(regex, string=v)):
            chandoan = k
            break
    return re.sub(r'^.*?:', '', chandoan).strip()

def get_text_by_block(response):
    document = response.full_text_annotation
    texts = []
    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                text = ''
                for word in paragraph.words:
                    for symbol in word.symbols:
                        text += symbol.text 
                    text += ' '
                text = re.sub(r'\s([.:;)])', r'\1', text)
                text = re.sub(r'([(-])\s', r'\1', text)
                texts.append(text.strip())
    return texts

def read_image(image_src:str):

    FOLDER_ROOT = str(pathlib.Path().absolute())
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= FOLDER_ROOT + r"\read_img\resource\client-key\client-key.json"
    with io.open(os.path.join(image_src), 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)
    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=image)

    res_para_list= get_text_by_block(response)
    para_list = tuple(unidecode.unidecode(string.strip()).upper() for string in res_para_list)

    res_string_list = tuple(string.strip() for string in response.text_annotations[0].description.split('\n'))
    str_list = tuple(unidecode.unidecode(string.strip()) for string in res_string_list)

    # Handle medicine dataframe
    thuoc_df = pd.read_excel(FOLDER_ROOT + r'\read_img\resource\keyword\danh-muc-thuoc-benh-vien-dai-hoc-y-duoc-hue.xlsx', header=None)
    thuoc_df = thuoc_df.dropna(how='all').dropna(how='all', axis=1)
    headers = thuoc_df.iloc[0]
    thuoc_df = pd.DataFrame(thuoc_df.values[1:], columns=headers)

    # Handle hospital dataframe
    bv_df = pd.read_excel(FOLDER_ROOT + r'\read_img\resource\keyword\List Bệnh viện ở Việt Nam (fill).xlsx')
    bv_df = bv_df.loc[:, ~bv_df.columns.str.contains('^Unnamed')]
    normalize_bv = bv_df.iloc[:, 0].apply(lambda x: unidecode.unidecode(str(x).upper()))
    hospital_dict= dict(zip(normalize_bv, bv_df.iloc[:, 0].apply(lambda x: re.sub(u'\xa0', ' ', x).strip())))

    hospital_name = get_hospital_name(str_list, hospital_dict, res_string_list)
    patient_age = get_patient_age(str_list=str_list, res_string_list=res_string_list)
    medicine_list = get_medicine(str_list=str_list, thuoc_df=thuoc_df, res_string_list=res_string_list)
    gender = get_gender(str_list=str_list, res_string_list=res_string_list)
    diagnose = get_diagnose(para_list=para_list, res_para_list=res_para_list)



    return {
        "hospital_name":hospital_name,
        "patient_age": patient_age, 
        "medicine_list": medicine_list,
        "gender": gender.capitalize(),
        "diagnose": diagnose
    }