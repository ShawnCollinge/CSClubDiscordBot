import aiohttp
from dotenv import load_dotenv
from os import getenv
load_dotenv()

async def convert(time):
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    unit = time[-1]
    if unit not in time_dict:
        return -1
    try:
        val = int(time[:-1])
    except: 
        return -1
    return val * time_dict[unit]

async def compile(language, version, code):
    url = "https://api.jdoodle.com/v1/execute"
    data = {
        "clientId": getenv("JDOODLE_ID"),
        "clientSecret": getenv("JDOODLE_SECRET"),
        "script": code,
        "language": language,
        "versionIndex": version
    }
    header = {
        'Content-Type': 'application/json; charset=UTF-8'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=header) as response:
            output = await response.json()
            if ("error" in output):
                return output['error']
            else:
                return output['output']