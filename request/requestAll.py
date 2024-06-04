import requests
import pandas as pd


# Define the function to fetch data
def request_all():
    all_data = []
    for i in range (1, 49):
        response = requests.get(f'https://esi.evetech.net/dev/universe/types/?datasource=tranquility&page={i}')
        if response.status_code != 200:
            print("Error fetching data")
            break
        data = response.json()
        all_data.extend(data)
    return all_data


# Define function to process data and save to Excel
def type_id():
    datas = request_all()

    data_list = []

    # Use tqdm for progress tracking
    for item in datas:
        response = requests.get(
            f'https://esi.evetech.net/dev/universe/types/{item}/?datasource=tranquility&language=en')
        data_item = response.json()
        name = data_item.get('name', '')
        type_id = data_item.get('type_id', '')
        description = data_item.get('description', '')
        print(f'{type_id}-{name}- {description}')
        data_list.append({'type_id': type_id, 'name': name})

        df = pd.DataFrame(data_list)
        df.to_excel('output.xlsx')


# data = request_all()
#
# # Сохраняем данные в Excel файл
# df = pd.DataFrame(data)
# df.to_excel('output2.xlsx')
type_id()