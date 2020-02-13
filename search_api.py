import requests
from urllib.parse import quote


def call(keyword, start):
    encText = quote(keyword)
    url = "https://openapi.naver.com/v1/search/webkr?query=" + encText + "&display=100" + "&start=" + str(start)
    result = requests.get(url=url, headers={"X-Naver-Client-Id":"XI45JOPUhLNDIiOBlooN",
                                          "X-Naver-Client-Secret":"XnY40nbqyJ"})
    print(result)  # Response [200]
    return result.json()

# 1000개의 검색 결과 받아오기
def get100results(keyword):
    list = []
    #for num in range(0,10):
        #list = list + call(keyword, num * 100 + 1)['items'] # list 안에 키값이 ’item’인 애들만 넣기
    list = list + call(keyword, 100 + 1)['items'] # list 안에 키값이 ’item’인 애들만 넣기
    return [ list[i]['link'] for i in range(len(list))]
    
    #for i in range(len(list)):
    #    yield list[i]['link'] 



 
