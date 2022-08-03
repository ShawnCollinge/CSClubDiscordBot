import os, WebsiteAPI, aiohttp

async def checkWeather(author:str, city):
    if city == "default":
        city = await WebsiteAPI.get_data(author)
        if city == False:
            return "Please select a valid city"
        else:
            city = city['city']
    
    params = {
            "appid": os.getenv("WEATHER_API"),
            "q": city,
            "units": "imperial"
            }
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.openweathermap.org/data/2.5/weather", params=params) as response:
            weather = await response.json()
    try:
        theMessage = f"the current weather for {city} is {weather['weather'][0]['description']} with a temperature of {weather['main']['temp']}"
    except KeyError:
        theMessage = "Invalid city"
    return theMessage

async def set_city(message, city):
    data = {
        "city": city
    }
    if (await WebsiteAPI.create_user(message.author.id, data)):
        return f"Successfully set city to {city}"
    else: 
        return f"Error with setting city to {city}"