from datetime import datetime, timedelta

import pygsheets

key_json = 'gsheets_key.json'


def find_row_number(ad_link, worksheet):
    try:
        # Authenticate using service account credentials
        # gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        # sheet = gc.open('FERC telegram bot overview')
        # worksheet = sheet[0]
        
        cells_list_of_lists = worksheet.find(str(ad_link), matchEntireCell=True)  # [[]]
        print(cells_list_of_lists)
        if cells_list_of_lists:  # empty list object considered as false
            return cells_list_of_lists[0].row
        else:
            return None
    except Exception as x:
        print(x)


iphone_model_worksheet_index = {
    'xr': 2,
    '11': 3
}


def insert_list_of_iphone_links(list_of_lists_of_item_rows, iphone_model):
    try:
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        # Convert the list of links into a single column

        # Open the Google Sheet by name
        sheet = gc.open('Loop browser bot — iphones db')
        # Select the first worksheet in the Google Sheet
        worksheet = sheet[iphone_model_worksheet_index[iphone_model]]
    
        # for index, link in enumerate(list_of_lists_of_item_rows, 1):
        #     row_number = index
        #     cell_address = f"A{row_number}"  # Column B, row specified by row_number
        #     worksheet.update_value(cell_address, link)

        worksheet.insert_rows(row=2, values=list_of_lists_of_item_rows)
    
    except Exception as x:
        print(x)


def get_list_of_iphone_links(iphone_model):
    # Authenticate using service account credentials
    gc = pygsheets.authorize(service_file=key_json)
    # Convert the list of links into a single column
    
    # Open the Google Sheet by name
    sheet = gc.open('Loop browser bot — iphones db')
    # Select the first worksheet in the Google Sheet
    worksheet = sheet[iphone_model_worksheet_index[iphone_model]]
    
    column_values = worksheet.get_col(3)

    # Extract links from the column values
    links = [value for value in column_values if value != '']
    
    return links


def initialize_conversation(title, price, ad_link, conv_id):
    # Authenticate using service account credentials
    gc = pygsheets.authorize(service_file=key_json)
    # Convert the list of links into a single column
    
    # Open the Google Sheet by name
    sheet = gc.open('Loop browser bot — iphones db')
    # Select the first worksheet in the Google Sheet
    worksheet = sheet[1]
    print('inside')
    if find_row_number(ad_link, worksheet) is None:
        print('inside if')
        now = datetime.now()
        epoch = datetime(1899, 12, 30)
        delta = now - epoch
        current_time = delta.days + (delta.seconds / 86400)
        
        conv_link = f'https://www.kufar.by/account/messaging/{conv_id}'
        values_to_insert = [[title, price, 'Сообщение отправлено', current_time, '', '', ad_link, conv_link]]
    
        last_row = worksheet.get_col(1, include_empty=False)
        # get the index of the first empty row
        last_row_index = len(last_row)
        
        print('before insert')
        worksheet.insert_rows(row=last_row_index, values=values_to_insert)
        print('after insert')
    print('outside')


def got_answer(ad_link, preview, time_received_str):
    # Authenticate using service account credentials
    gc = pygsheets.authorize(service_file=key_json)
    # Convert the list of links into a single column
    
    # Open the Google Sheet by name
    sheet = gc.open('Loop browser bot — iphones db')
    # Select the first worksheet in the Google Sheet
    worksheet = sheet[1]
    
    row_number = find_row_number(ad_link, worksheet)
    
    if row_number is not None:
        now = datetime.strptime(time_received_str, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=3)
        epoch = datetime(1899, 12, 30)
        delta = now - epoch
        time_received = delta.days + (delta.seconds / 86400)

        time_col_index = 5
        worksheet.update_value((row_number, time_col_index), time_received)
        
        preview_col_index = 6
        worksheet.update_value((row_number, preview_col_index), preview)
        
        status_col_index = 3
        worksheet.update_value((row_number, status_col_index), 'Получен ответ')


if __name__ == '__main__':
    initialize_conversation('edvbwrbw  wvwvgfqwe', 4, 'https://www.kufar.by/account/messaging/8e8', 563463463)
    got_answer(5, 'ff', '2023-08-30T11:49:03Z')
    