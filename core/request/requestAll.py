import aiohttp
import asyncio
import pandas as pd


async def fetch_data(session, page):
    async with session.get(
        f"https://esi.evetech.net/dev/universe/types/?datasource=tranquility&page={page}"
    ) as response:
        return await response.json()


async def main():
    all_data = []
    async with aiohttp.ClientSession() as session:
        for i in range(1, 49):
            data = await fetch_data(session, i)
            if not data:
                print("Error fetching data")
                break
            all_data.extend(data)

    data_list = []
    for item in all_data:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://esi.evetech.net/dev/universe/types/{item}/?datasource=tranquility&language=ru"
            ) as response:
                data_item = await response.json()
                print(data_item)
                # name = data_item.get('name', '')
                # type_id = data_item.get('type_id', '')
                # description = data_item.get('description', '')
                # print(f'{type_id}-{name}- {description}')
                # data_list.append({'type_id': type_id, 'name': name})

    # df = pd.DataFrame(data_list)
    # df.to_excel('output.xlsx')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
