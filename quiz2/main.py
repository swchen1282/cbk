import time
import requests
import configparser
import json
import math
from mongo_insert import mongo_insert
import re
from logger import create_logger
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
"""
This module handle crawler and inert into mongo DB
"""

logger = create_logger()
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


def get_sex_condition(cond: str) -> str:
    result = re.search('(all_sex)|(girl)|(boy)', cond)
    if result:
        return result[0]
    else:
        return 'unknown'


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
    try:
        for i in regions.keys():
            logger.info(f'current regions is: {regions.get(i)}')
            pages_url = f'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region={i}'
            total_pages = get_total_pages(pages_url)
            total_pages = 10  # for dev
            for page in range(1, total_pages + 1):
                logger.info(f'current pages/total: {page}/{total_pages}')
                detail_url = f'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region={i}&firstRow={page * 30}'
                main_page = requests.get(detail_url, headers=header_main)
                detail_data = json.loads(main_page.text).get('data').get('data')

                # filter column
                filtered_data = [dict((k, v) for k, v in d.items() if k in filter_column) for d in detail_data]  # use list comprehension to filter list of dicts

                # use filter column's id to request detail page and get phone/mobile/url
                # link_info = [map(get_contact_url, d['id']) for d in filtered_data]

                # handling sex column
                sex_condition = [get_sex_condition(x['condition']) for x in filtered_data]
                for j in range(len(filtered_data)):
                    filtered_data[j].update({'sex_condition': sex_condition[j]})
                    filtered_data[j].pop('condition')
                time.sleep(2)

                # insert to mongo
                # mongo_insert(filtered_data)
                logger.info(f'insert pages{page} successfully')
    except Exception as e:
        logger.exception(e)
        raise


if __name__ == '__main__':
    main()
