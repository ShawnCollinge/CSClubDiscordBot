# CSClubDiscordBot
Discord bot for shoreline's cs club

If you want to use this bot you will need to fill in the info in .env.example and change the file to just .env, you will also have to install the requirements in requirements.txt with pip3 install -r requirements.txt


Currently has the following commands:

!setcity <city> - sets your default city for the !weather command.
!weather [city] - uses open weather api to return the current weather in the specified city. If no city is specified it will pull your default city
!kanye - returns a kanye quote from kanye rest api - https://kanye.rest/
!meme - returns a random post from reddit.com/r/programmerhumor
!remindme <time(s/m/h/d/w)> <msg> - will tag you in a reminder message after a specified time in your command
!poll <item1> or <item2> - puts up a poll with 2 items for people to choose between
!rules - sends a message to the channel of the rules located in rules.txt

admin commands - 
!kick <member> [reason] - kicks member from the server
!ban <member> [reason] - bans member from the server
!clear [number] - will clear the number specified of messages from chat (default is 2)
!unban <member> - will unban the member
!whois <member> - will return a whois on the member.
