import itertools
import os
import threading
import time
import concurrent.futures

import pygsheets.exceptions
from dotenv import load_dotenv, find_dotenv
import random

import requests
from bs4 import BeautifulSoup
import gsheets
import tg

load_dotenv(find_dotenv())


# Iterate through the elements and extract the necessary information

# iphone_models = ['xr', '11']

# iphone_model_memory_price_dict = {
#     'xr_64': 400,
#     'xr_128': 500,
#     '11_64': 600,
#     '11_128': 700
# }


def get_item_rows(iphone_model):
    list_of_lists_of_items = []
    
    response = requests.get(
        f'https://www.kufar.by/l/r~minsk/mobilnye-telefony/mt~apple?cmp=0&oph=1&query=iphone+{iphone_model}&sort=lst.d')
    
    html_text = response.text
    
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Find all elements with the specified class
    elements = soup.find_all('a', class_='styles_wrapper__5FoK7')
    
    for index, element in enumerate(elements):
        try:
            ad_plank = element.find('div', class_='styles_badge__rxNZ4')
            if ad_plank:
                continue
            
            price = element.find('p', class_='styles_price__G3lbO').get_text()
            title = element.find('h3', class_='styles_title__F3uIe').get_text()
            location = element.find('div', class_='styles_secondary__MzdEb').p.get_text()
            href = element['href']
            
            list_of_lists_of_items.append([title, price, href[:35], location, iphone_model])
        
        except AttributeError:
            pass
    
    return list_of_lists_of_items


def start_conversation(ad_link, message, model, price):
    url = "https://api.kufar.by/messaging-api/v1/conversations"
    
    headers = {
        "authority": "api.kufar.by",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"{os.getenv('BEARER-TOKEN')}",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://www.kufar.by",
        "pragma": "no-cache",
        "referer": "https://www.kufar.by/",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "x-app-name": "Web Kufar",
        "x-rudder-anonymous-id": f"{os.getenv('RUDDER-ANONYMOUS-ID')}"
    }
    
    data = {
        "ad_id": int(ad_link[26:]),
        "message": {
            "text": message
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        json_response = response.json()
        conversation_id = json_response['conversation_id']
        
        gsheets.initialize_conversation(model, price, ad_link, conversation_id)
        print(response.text)
        return conversation_id
    
    except KeyError:
        pass


def check_messages():
    headers = {
        'authority': 'api.kufar.by',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f"{os.getenv('BEARER-TOKEN')}",
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.kufar.by',
        'pragma': 'no-cache',
        'referer': 'https://www.kufar.by/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'x-app-name': 'Web Kufar',
        'x-rudder-anonymous-id': f"{os.getenv('RUDDER-ANONYMOUS-ID')}"
    }
    
    params = {
        'limit': '100',
        'offset': '0',
    }
    
    response = requests.get('https://api.kufar.by/messaging-api/v1/conversations', params=params, headers=headers)
    
    json_response = response.json()
    
    conversations = json_response['conversations']
    
    if conversations:
        
        ad_links_with_empty_answers = gsheets.get_ad_links_with_empty_answer()
        
        for conversation in conversations:
            if int(conversation['unseen']) > 0:
                try:
                    unseen_conv_id = conversation['conversation_id']
                    unseen_conv_last_message_preview = conversation['last_message']['preview']
                    unseen_conv_last_message_sender_id = conversation['last_message']['sender_id']
                    unseen_conv_last_message_sent_time = conversation['last_message']['timestamp']
                    unseen_conv_ad_link = conversation['ad_info']['link']
                    
                    if unseen_conv_ad_link in ad_links_with_empty_answers:
                        gsheets.got_answer(unseen_conv_ad_link, unseen_conv_last_message_preview,
                                           unseen_conv_last_message_sent_time)
                
                except Exception:
                    pass


def get_iphone_memory(link):
    response = requests.get(link)
    
    html_text = response.text
    
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Find all elements with the specified class
    value_elements = soup.find_all('div', class_='styles_parameter_value__BkYDy')
    key_elements = soup.find_all('div', class_='styles_parameter_label__i_OkS')
    for index, element in enumerate(key_elements):
        if element.text == 'Память':
            print(value_elements[index].span.get_text())
            memory_str = value_elements[index].span.get_text()
            list_from_string = memory_str.split(' ')
            return list_from_string[0]


greeting_options = [
    'Здравствуйте',
    'Приветствую',
    'Доброго времени суток',
]
interesting_offer_options = [
    '',
    'Заинтересовало Ваше предложение',
    'Я заинтересован в покупке Вашего телефона',
    'Заинтересовал Ваш телефон',
    'Увидел Ваше объявление',
    'Заинтересовало Ваше объявление',
    'Ваше предложение привлекло мое внимание.',
    'Хотел бы обсудить возможность приобретения вашего телефона',
    'Мне интересен ваш телефон',
    'Обратил внимание на ваше объявление',
    'Ваше объявление вызвало у меня интерес',
    'Обратил внимание на ваше предложение',
    'Ваш телефон показался мне интересным',
    'Ваше объявление показалось мне интересным',
]
how_to_reach_options = [
    'По какому номеру с Вами можно связаться',
    'По какому номеру с Вами можно поговорить',
    'Как могу с Вами связаться',
    'Как я могу с Вами связаться',
    'Как можно с Вами связаться',
    'Могли бы Вы дать Ваш номер телефона',
    'Не могли бы Вы дать Ваш контакт',
    'Могли бы Вы оставить свой контактный номер телефона',
    'Могли бы Вы оставить свой контактный номер телефона для связи',
    'Не могли бы Вы оставить свой контактный номер телефона',
    'Не могли бы Вы оставить свой контактный номер телефона для связи',
]
where_to_see_options = [
    'И где можно посмотреть в самое ближайшее время',
    'И где можно посмотреть в ближайшее время',
    'И где можно посмотреть телефон в ближайшее время',
    'И где можно посмотреть телефон в самое ближайшее время',
    'И по какому адресу можно посмотреть телефон',
    'И по какому адресу можно посмотреть телефон в ближайшее время',
    'И по какому адресу можно посмотреть телефон в самое ближайшее время',
    'И в каком районе можно посмотреть телефон',
    'И в каком районе можно посмотреть телефон в ближайшее время',
    'И в каком районе можно посмотреть телефон в самое ближайшее время',
    'И в каком районе можно посмотреть телефон',
    'И подскажите, где могу посмотреть телефон сегодня',
    'И подскажите, где могу посмотреть телефон сегодня или завтра',
    'И подскажите, пожалуйста, где могу посмотреть телефон сегодня',
    'И подскажите, пожалуйста, где могу посмотреть телефон сегодня или завтра',
]

symbols = [
    '.',
    '..',
    '!',
    '!!'
]


def start_kufar_conversation(new_items_rows_):
    for new_item_row in new_items_rows_:
        item_title = new_item_row[0]
        item_price = new_item_row[1]
        item_link = new_item_row[2]
        item_model = new_item_row[4]
        
        item_memory = get_iphone_memory(item_link)
        print(item_memory)
        if item_memory is None or item_memory == 'None':
            item_max_price = '999999'
        else:
            try:
                item_max_price = model_memory_price_dict[f'{item_model}_{item_memory}']
            except KeyError as x:
                print(x)
                continue
            
        try:
            if int(item_price[:-3]) <= int(item_max_price):
                start_message = (f"{random.choice(greeting_options)}{random.choice(symbols)} "
                                     f"{random.choice(interesting_offer_options)}{random.choice(symbols)} "
                                     f"{random.choice(how_to_reach_options)}? {random.choice(where_to_see_options)}?")
                    
                conversation_id = start_conversation(item_link, start_message, item_title, item_price)
                if conversation_id:
                    tg.send_message(f'{item_title}\nПамять:{item_memory}\nЦена:{item_price}\n{item_link}')
                    
                time.sleep(4)
        except Exception as x:
            tg.send_message_to_admin(x)


def go(model_):
    try:
        list_of_saved_items = gsheets.get_list_of_iphone_links(model_)
    except pygsheets.exceptions.WorksheetNotFound:
        list_of_saved_items = []
        
    list_of_lists_of_new_request_items = get_item_rows(model_)
    tg.send_message_to_admin('got everything from gsheets')
    # list_of_new_items = [x[2] for x in list_of_lists_of_new_request_items]
    
    new_items_rows = [item_row for item_row in list_of_lists_of_new_request_items if
                      item_row[2] not in list_of_saved_items]

    new_items_rows_str = list()
    for new_item_row in new_items_rows:
        new_items_rows_str.append('--'.join(new_item_row))
        
    tg.send_message_to_admin('\n\n'.join(new_items_rows_str))
    
    if new_items_rows:
        item_rows_thread = threading.Thread(target=start_kufar_conversation, args=(new_items_rows,))
        item_rows_thread.start()
        # executor.submit(start_kufar_conversation, new_items_rows)

    tg.send_message_to_admin('after start conversation')
    
    gsheets.insert_list_of_iphone_links(list_of_lists_of_new_request_items, model_)
    
    tg.send_message_to_admin('after inserting new links to gsheets')
    
    # check_messages_thread = threading.Thread(target=check_messages)
    # check_messages_thread.start()

    tg.send_message_to_admin('after checking messages')


if __name__ == '__main__':
    while True:
        tg.send_message_to_admin('very beggining')
        model_memory_price_dict = dict()
        threads = list()
        model_memory_price_list = gsheets.get_model_memory_price_list()
        
        for model_memory_price in model_memory_price_list:
            model_for_price = model_memory_price[0]
            memory_for_price = model_memory_price[1]
            price_for_price = model_memory_price[2]
            
            model_memory_price_dict[f'{model_for_price}_{memory_for_price}'] = price_for_price
        
        tg.send_message_to_admin('model_price list created')
        print(model_memory_price_dict)
        
        unique_models = set([x[0] for x in model_memory_price_list])
        for global_item_model in unique_models:
            tg.send_message_to_admin(f'go for {global_item_model}')
            go_thread = threading.Thread(target=go, args=(global_item_model,))
            threads.append(go_thread)
            go_thread.start()
        
        for thread in threads:
            thread.join()
            tg.send_message_to_admin('threads are gathered')
            
        time.sleep(20)

# gsheets.get_list_of_iphone_links()
# get_item_ids()
# gsheets.insert_list_of_iphone_links(list_of_item_ids)
# gsheets.get_list_of_iphone_links()
