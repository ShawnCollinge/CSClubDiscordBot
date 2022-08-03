import os, aiohttp, asyncio
from dotenv import load_dotenv

LINK = "http://127.0.0.1:3000/api/"

async def get_data(username):
    api_link = f"{LINK}{os.getenv('WEBSITE_API')}"
    params = {
        "username": username
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(api_link, data=params) as response:
            code = response.status
            if code == 404 or code == 403:
                return False
            else:
                return await response.json()

async def create_user(username, data):
    api_link = f"{LINK}{os.getenv('WEBSITE_API')}"
    data['username'] = username
    async with aiohttp.ClientSession() as session:
        if (await get_data(username) == False):
            async with session.post(api_link, data=data) as response:
                code = response.status
                return code == 200
        else:
            async with session.patch(api_link, data=data) as response:
                code = response.status
                return code == 200
        

async def is_bot_admin(username):
    return get_data(username)['admin']

# # bot admin
# async def delete_user(message_data):
#     api_link = f"{LINK}{os.getenv('WEBSITE_API')}"
#     data_to_return = {
#         "is_admin": is_bot_admin(message_data.author),
#         "user": message_data.content[9:],
#     }
#     if (data_to_return['is_admin']):
#         async with aiohttp.ClientSession() as session:
#             async with session.delete(api_link, data={"username": data_to_return['user']}) as response:
#                 code = response.status
#                 data_to_return['success'] = (code == 200)
#     return data_to_return