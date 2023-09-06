import itertools
import threading
import time
import concurrent.futures

import requests
from bs4 import BeautifulSoup
import gsheets
import tg

# Iterate through the elements and extract the necessary information

iphone_models = ['xr', '11']

iphone_model_memory_price_dict = {
    'xr_64': 400,
    'xr_128': 500,
    '11_64': 600,
    '11_128': 700
}


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
            
            list_of_lists_of_items.append([title, price, href[:35], location])
            
        except AttributeError:
            pass
        
    return list_of_lists_of_items


def start_conversation(ad_link, message, model, price, offer_price):
    url = "https://api.kufar.by/messaging-api/v1/conversations"
    
    headers = {
        "authority": "api.kufar.by",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InYyMCIsInNjaHYiOiIyIiwidHlwIjoiSldUIn0.eyJhaWQiOiI4MDExNzg0IiwiY2FkIjpmYWxzZSwiZGlkIjoiZWIxNTcwYTdlNDY4NjcxZTM1OWIzY2IyMzlmZTZlN2EiLCJleHAiOjE3MjU1MzA2ODYsImlhdCI6MTY5MzM4OTg4NiwianRpIjoiODAxMTc4NDplM1Eza1NiMCIsInB0ciI6ZmFsc2UsInR5cCI6InVzZXIifQ.b0g9gFbgL2GdF8TsSbl0NUb3aE_MsVXuol0_yV2vSOg",
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
        "x-rudder-anonymous-id": "de9e3cf0-47d9-4903-8209-b845043c132a"
    }
    
    print(offer_price, 'offer price!!!!!!!!!')
    
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
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InYyMCIsInNjaHYiOiIyIiwidHlwIjoiSldUIn0.eyJhaWQiOiI4MDExNzg0IiwiY2FkIjpmYWxzZSwiZGlkIjoiZWIxNTcwYTdlNDY4NjcxZTM1OWIzY2IyMzlmZTZlN2EiLCJleHAiOjE3MjU1MzA2ODYsImlhdCI6MTY5MzM4OTg4NiwianRpIjoiODAxMTc4NDplM1Eza1NiMCIsInB0ciI6ZmFsc2UsInR5cCI6InVzZXIifQ.b0g9gFbgL2GdF8TsSbl0NUb3aE_MsVXuol0_yV2vSOg',
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
        'x-rudder-anonymous-id': 'de9e3cf0-47d9-4903-8209-b845043c132a',
    }
    
    params = {
        'limit': '100',
        'offset': '0',
    }
    
    response = requests.get('https://api.kufar.by/messaging-api/v1/conversations', params=params, headers=headers)
    
    json_response = response.json()
    
    conversations = json_response['conversations']
    
    if conversations:
        for conversation in conversations:
            if int(conversation['unseen']) > 0:
                try:
                    unseen_conv_id = conversation['conversation_id']
                    unseen_conv_last_message_preview = conversation['last_message']['preview']
                    unseen_conv_last_message_sender_id = conversation['last_message']['sender_id']
                    unseen_conv_last_message_sent_time = conversation['last_message']['timestamp']
                    unseen_conv_ad_link = conversation['ad_info']['link']
                    
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
    
    
def start_kufar_conversation(new_items_rows_):
    for new_item_row in new_items_rows_:
        item_title = new_item_row[0]
        item_price = new_item_row[1]
        item_link = new_item_row[2]
        
        item_memory = get_iphone_memory(item_link)
        
        message_text = f'{item_title}:\n\nПамять: {item_memory} ГБ\n\n{item_price}\n\n{item_link}'
        tg.send_message(message_text)
        
    for new_item_row in new_items_rows_:
        item_title = new_item_row[0]
        item_price = new_item_row[1]
        item_link = new_item_row[2]
        
        item_memory = get_iphone_memory(item_link)
        try:
            item_offer_price = iphone_model_memory_price_dict[f'{iphone_model_name}_{item_memory}']
            
            start_conversation(item_link, 'Добрый день, заинтересовало Ваше предложение. '
                                          'По какому номеру с Вами можно связаться? '
                                          'И где можно посмотреть в самое ближайшее время?', item_title,
                               item_price, item_offer_price)
            time.sleep(40)
        
        except KeyError:
            pass


if __name__ == '__main__':
    for iphone_model_name in itertools.cycle(iphone_models):
        list_of_saved_items = gsheets.get_list_of_iphone_links(iphone_model_name)
        list_of_lists_of_new_request_items = get_item_rows(iphone_model_name)
        # list_of_new_items = [x[2] for x in list_of_lists_of_new_request_items]
        
        new_items_rows = [item_row for item_row in list_of_lists_of_new_request_items if item_row[2] not in list_of_saved_items]
        print(new_items_rows, 'new_items!!')
        
        if new_items_rows:
            item_rows_thread = threading.Thread(target=start_kufar_conversation, args=(new_items_rows, ))
            item_rows_thread.start()
            # executor.submit(start_kufar_conversation, new_items_rows)
                
        print('after start conv')
                
        gsheets.insert_list_of_iphone_links(list_of_lists_of_new_request_items, iphone_model_name)
        check_messages_thread = threading.Thread(target=check_messages)
        check_messages_thread.start()
        
        time.sleep(20)
        
        
# gsheets.get_list_of_iphone_links()
# get_item_ids()
# gsheets.insert_list_of_iphone_links(list_of_item_ids)
# gsheets.get_list_of_iphone_links()
