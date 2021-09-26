## quiz1

- How to transfer chinese strings to integer
  - You should clean and prepare data first then use list comprehension to handle column
- 

## quiz2

### step flow

1. craw pages from https://rent.591.com.tw/?kind=0&region=1 and https://rent.591.com.tw/?kind=0&region=3
2. get the number of items of each page and iterate it to open the url
   1. get the column and data and ready to insert into `mongoDB`
   2. schema:
        ```
        物件編號 id
        物件名 address_img_title
        物件網址 url -> you should cominbe id by yourself
        縣市 region_name
        出租者 linkman
        出租者身分 role_name
        聯絡電話 phone/mobile -> you should craw another detail page to get info
        型態 shape
        現況 kind
        性別要求 you should find on condition: all_sex, girl, boy
        ```
3. Build mongoDB  

```sh
sudo docker-compose up

sudo ufw allow 27017/tcp  # open firewall on host
```

4. Build fast-api

### query filter
- region_name
- contact(phone/mobile)
- sex
- role_name
- linkman


### set env
PYTHONPATH=/home/swc/job_hunt/cathay_bank/quiz2/app

### start fast-api server
uvicorn app:cathay_api --reload --port=5000
