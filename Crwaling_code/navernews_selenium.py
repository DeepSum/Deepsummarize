import datetime

from selenium import webdriver
import pandas as pd

# import requests
# from bs4 import BeautifulSoup

# geckodriver: https://github.com/mozilla/geckodriver/releases
# chromedriver: https://chromedriver.chromium.org/downloads

#####################################
#####################################

section_id = "102"
# dates = ["20200901"]

start_date = "2020-08-01"
end_date = "2020-10-31"

# driver_path = '/home/aiffel0042/Documents/aiffel_local/geckodriver'
driver_path = '/home/aiffel0042/Documents/aiffel_local/chromedriver'

#####################################
#####################################

def get_list(date, sid, include_desc=True):
    def scrap(url, prev_data):
        print('current URL: ' + url)

        driver.get(url)
        parts = driver.find_element_by_id('main_content').find_element_by_class_name('list_body').find_elements_by_tag_name('ul') # .find_elements_by_class_name('type06_headline').find_elements_by_tag_name('li')

        # result = []
        result = prev_data

        for part in parts:
            data = part.find_elements_by_tag_name('li')
            # print(len(data))

            driver2 = webdriver.Chrome(driver_path)

            for item in data:
                curr_item = {}

                for elem in item.find_elements_by_tag_name('dt'):
                    # print(elem.get_attribute('class'))
                    if elem.get_attribute('class') == None or elem.get_attribute('class') == "":
                        curr_item['title'] = elem.text.strip()
                        curr_item['permalink'] = elem.find_element_by_tag_name('a').get_attribute('href')
                        curr_item['item_id'] = curr_item['permalink'].split('aid=')[1].split('&')[0]
                        curr_item['provider_id'] = curr_item['permalink'].split('oid=')[1].split('&')[0]
                        curr_item['section_id'] = curr_item['permalink'].split('sid1=')[1].split('&')[0]
                        break
                
                curr_item['provider_name'] = item.find_element_by_tag_name('dd').find_element_by_class_name('writing').text

                if include_desc:
                    print('current permalink: ', curr_item['permalink'])

                    # TODO: 기사 내용 및 입력시간 수집
                    '''
                    response = requests.get(curr_item['permalink'], verify=False)
                    soup = BeautifulSoup(response.text, 'html.parser')

                    curr_item['description'] = soup.find('div', {'id': "articleBody"}).find('div', {'id': "articleBodyContents"}).text
                    curr_item['datetime'] = soup.find('div', {'class': "article_header"}).find('div', {'class': "article_info"}).find('div', {'class': "sponsor"}).find('span', {'class': "t11"}).text
                    '''
                    
                    driver2.get(curr_item['permalink'])
                    curr_response_url = ""

                    for mt in driver2.find_elements_by_tag_name('meta'):
                        if mt.get_attribute('property') == 'og:url':
                            print(mt.get_attribute('content'))
                            curr_response_url = mt.get_attribute('content')
                            break
                    
                    if 'entertain.' in curr_response_url:
                        print("entertain is here!!!")
                        continue
                    elif 'sports.' in curr_response_url:
                        print("sports is here!!!")
                        continue

                    curr_item['description'] = driver2.find_element_by_id("articleBodyContents").text
                    curr_item['datetime'] = driver2.find_element_by_class_name("article_header").find_element_by_class_name("article_info").find_element_by_class_name("sponsor").find_elements_by_class_name("t11")[0].text

                print(curr_item)
                result.append(curr_item)

            driver2.close()

        print('# of articles: ', len(result))

        curr_page = int(driver.find_element_by_class_name('paging').find_element_by_tag_name('strong').text)
        pages = driver.find_element_by_class_name('paging').find_elements_by_tag_name('a')

        # print(pages)
        print(pages[len(pages) - 1].text)

        if not '다음' in pages[len(pages) - 1].text and curr_page > int(pages[len(pages) - 1].text):
            print("completed.")
            driver.close()
            return result
        else:
            for page in pages:
                next_page = int(page.get_attribute('href').split('page=')[1].split('&')[0])

                if next_page == curr_page + 1:
                    return scrap(page.get_attribute('href'), result)

        return result

    init_url = "https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=" + sid + "&date=" + date
    # driver = webdriver.Firefox(executable_path=driver_path)
    driver = webdriver.Chrome(driver_path)

    # result = scrap(init_url)
    result = scrap(init_url, [])

    return result



dates = []

# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.date_range.html
for d in pd.date_range(start=start_date, end=end_date):
    dates.append(datetime.datetime.strftime(d, "%Y%m%d"))

result = []
curr_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

for date in dates:
    data = get_list(date, section_id, True)
    result = result + data

    pd.DataFrame(data).to_csv('navernews_selenium_' + str(date) + '_' + curr_timestamp + '.csv', sep='\t')

pd.DataFrame(result).to_csv('navernews_selenium_' + str(date) + '.csv', sep='\t')