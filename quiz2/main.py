import time
import requests
from bs4 import BeautifulSoup
import configparser
import json
import math
from mongo_insert import mongo_insert
"""
This module handle crawler and inert into mongo DB
"""
config = configparser.ConfigParser()
config.read('./env.conf', encoding='UTF-8')
header_main = config._sections.get('header_main')
header_detail = config._sections.get('header_detail')
regions = {
    '1': '台北市',
    '3': '新北市',
}
filter_column = ['id', 'address_img_title', 'region_name', 'linkman', 'role_name', 'shape', 'kind', 'condition']
# https://rent.591.com.tw/home/{id} detail page


def get_contact_url(obj_id) -> dict:
    """
    Get linkman (renter) mobile from detail page, and generate detail page url by obj_id
    :param obj_id: selling object's id
    :return: mobile number of linkman(renter)
    """
    detail_url = f'https://rent.591.com.tw/home/{obj_id}'
    data_url = f'https://bff.591.com.tw/v1/house/rent/detail?id={obj_id}'
    data = json.loads(requests.get(data_url, headers=header_detail).text)
    result = {
        'phone': data.get('data').get('linkInfo').get('phone'),
        'mobile': data.get('data').get('linkInfo').get('mobile'),
        'url': detail_url,
    }
    return result


def get_total_pages(url: str) -> int:
    """
    Get total pages of url.

    :param url: 591 rent house url
    :return: total pages
    """
    res = json.loads(requests.get(url, headers=header_main).text)
    total_record = int(res.get('records').replace(',', ''))
    return math.ceil(total_record/30)


def main():
    # init the empty result list of dicts to insert
    result = [
        {
            'title': '',
            'url': '',
        }
    ]

    try:
        for i in regions.keys():
            pages_url = f'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region={i}'
            # total_pages = get_total_pages(pages_url)
            total_pages = 1  # for dev
            for page in range(1, total_pages + 1):
                detail_url = f'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region={i}&firstRow={page * 30}'
                main_page = requests.get(detail_url, headers=header_main)
                detail_data = json.loads(main_page.text).get('data').get('data')

                # filter column
                # filtered_data = dict((k, v) for k, v in detail_data[0].items() if k in filter_column)
                filtered_data = [dict((k, v) for k, v in d.items() if k in filter_column) for d in detail_data]  # use list comprehension to filter list of dicts
                # print(filtered_data)

                # use filter column's id to request detail page and get phone/mobile/url
                # link_info = [map(get_contact_url, d['id']) for d in filtered_data]

                # list(map(get_contact_url, [x['id'] for x in filtered_data]))
                # link_info = [d for d in filtered_data]
                # get_contact_url(filtered_data[0].get('id'))
                # print(get_contact_url(filtered_data[0].get('id')))

                # insert to mongo
                mongo_insert(filtered_data)
    except:
        raise
    # try:
    #     for page in range(1, 3):
    #         soup_main = BeautifulSoup(browser.page_source, 'html.parser')  # lxml in my project
    #         elements_main = soup_main.find_all('li', {'class': 'pull-left infoContent'})
    #         print(f'==========current pages: {page}/{3}==========')
    #         for element_main in elements_main:
    #             title = element_main.find('h3').find('a').getText().strip()
    #             url = element_main.find('h3').find('a').get('href').strip()
    #             url = 'https://rent.591.com.tw/home/11389423'
    #             # id = f"R{re.search(r'(?<=rent-detail-).*(?=.html)', url)[0]}"
    #             browser.execute_script(f"window.open('{url}', '_blank');")  # open each selling detail page on new tab
    #             browser.switch_to.window(browser.window_handles[1])  # make sure you switch to the detail page
    #             # get detail info here
    #             detail_html = requests.get(url).text
    #             soup_detail = BeautifulSoup(detail_html, 'html.parser')
    #             print(soup_detail)
    #             # get detail info here
    #             browser.close()  # close detail page and continue to next detail page on main_page
    #
    #             if page != 463:
    #                 page_next = browser.find_element_by_class_name(
    #                     'pageNext')  # 下一頁按鈕的樣式類別(class)為「pageNext」後，就可以利用Selenium套件進行元素的定位與點擊換頁了
    #                 page_next.click()
    #                 time.sleep(3)
    # except:
    #     browser.quit()
    #     raise
    # finally:
    #     print('finish all the crawler')


if __name__ == '__main__':
    main()
