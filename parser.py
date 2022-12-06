import asyncio
import datetime
import json

import aiohttp as aiohttp
import pandas as pd


async def get_product_ids_v2(keyword: str, num_products: int):
    roots_check = []
    async with aiohttp.ClientSession() as session:
        page = 1
        roots = []
        count_of_feedback = 0
        while True:
            # print(f"Товары с {page} страницы", sep="\n")
            url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,7,3,6,5,18,21&dest=-1216601,-337422,-1114902,-1198055&emp=0&lang=ru&locale=ru&page={page}&pricemarginCoeff=1.0&query={keyword}&reg=0&resultset=catalog&sort=rate&suppressSpellcheck=false"
            response = await session.get(url=url)
            list_of_items = json.loads(await response.text())
            if len(roots) >= num_products or len(list_of_items) == 0:
                break
            for item in list_of_items['data']['products']:
                if item['root'] not in roots_check:
                    roots_check.append(item['root'])
                    roots.append({"root": item['root'], "numberOfFeedbacks": item['feedbacks']})
                    count_of_feedback += item['feedbacks']
                    if len(roots) >= num_products:
                        break
            page += 1
    print(f"Всего товаров: {len(roots)}", f"Всего отзывов: {count_of_feedback}", sep="\n")
    return roots


async def get_product_feedback(imtId: int, skip: int, session):
    json_data = {
        "imtId": imtId,
        "skip": skip,
        "take": 30,
        "order": "dateDesc"
    }

    url = "https://feedbacks.wildberries.ru/api/v1/summary/full"
    headers = {"Content-Type": "application/json"}
    response = await session.post(url=url, json=json_data, headers=headers)
    # print(f"Отбработал {imtId}: {skip}-{skip + 30}")
    if "ErrorCode" not in await response.text():
        return json.loads(await response.text())['feedbacks']
    else:
        return None


async def get_product_ids():
    query = {"subject": "518;593;924;1407;2913;3001;6817"}
    url = "https://catalog.wb.ru/catalog/electronic2/catalog"

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, params=query)
        list_of_items = json.loads(await response.text())
    roots = []
    count_of_feedback = 0
    for item in list_of_items['data']['products']:
        roots.append({"root": item['root'], "numberOfFeedbacks": item['feedbacks']})
        count_of_feedback += item['feedbacks']

    print(f"Всего товаров: {len(roots)}", f"Всего отзывов: {count_of_feedback}", sep="\n")
    return roots


async def get_feedbacks(keyword: str, num_products: int):
    print(f"\nПоиск по слову: {keyword}")
    start_time = datetime.datetime.now()
    # products = await get_product_ids()
    products = await get_product_ids_v2(num_products=num_products, keyword=keyword)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for product in products:
            for i in range(0, product['numberOfFeedbacks'], 30):
                task = asyncio.create_task(get_product_feedback(imtId=product['root'], skip=i, session=session))
                tasks.append(task)
        data = await asyncio.gather(*tasks)

    count = 0
    count_fb = 0
    feedbacks_list = []
    print("Выгрузка завершена! Начал считать...")
    for response in data:
        if response is not None:
            count_fb += len(response)
            count += 1
            feedbacks_list.extend(response)
    print("Начал записывать в CSV...")
    df = pd.json_normalize(feedbacks_list)
    df.to_csv("parsed_feedbacks.csv", sep=';', encoding='utf-8')
    print(f"\nВыполнилось у {count} из {len(data)}. Общее количество: {count_fb}\nЗатрачено времени: {(datetime.datetime.now() - start_time)}")


if __name__ == '__main__':
    print("Введите слово для поиска: ")
    word = str(input())
    print("Введите количество выгружаемых товаров: ")
    count = int(input())

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_feedbacks(keyword=word, num_products=count))
    loop.run_until_complete(future)
