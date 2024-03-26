import discord, random, asyncpraw, aiohttp, asyncio, helper, Weather, WebsiteAPI, os, sys, git, pytz, apscheduler
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, filename='bot_errors.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


load_dotenv()

reddit = asyncpraw.Reddit(client_id = getenv("REDDIT_CLIENT_ID"),
                    client_secret = getenv("REDDIT_CLIENT_SECRET"),
                    user_agent = getenv("REDDIT_USER_AGENT"))

g = git.cmd.Git(os.path.dirname(os.path.realpath(__file__)))
intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix=os.getenv("COMMAND"), intents=intents)
long_homework = ["individual assignment", "long homework"]
already_sent = {"long_homework": False, "noice": False}
announce_id = 895806644578025516
tz = pytz.timezone('America/Los_Angeles')
scheduler = AsyncIOScheduler(timezone=tz)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(msg):
    if (msg.author.bot):
        return
    global already_sent
    if msg.channel.id == announce_id:
        data = {
            "_id": msg.id,
            "message": msg.clean_content,
            "type": "announcement",
            "author": msg.author.name,
            "date": date.today()
        }
        await WebsiteAPI.add_data(data)
    if "lol" in msg.content:
        if (random.randint(0,10) == 2):
            await msg.channel.send("https://c.tenor.com/ASGuOCPGrKEAAAAd/kekw-kek.gif")
    if "noice" == msg.content:
        if not already_sent["noice"]:
            await msg.channel.send("https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/thematedkid/phpPlfUuy.gif")
            already_sent["noice"] = True
            await asyncio.sleep(60)
            already_sent["noice"] = False

    await bot.process_commands(msg)

@bot.command()
async def rules(ctx):
    with open("rules.txt", encoding = 'utf-8') as f:
        await ctx.channel.send(f.read())

@bot.command(aliases = ["pl"])
async def poll(ctx,*,msg):
    channel = ctx.channel
    try:
        op1, op2 = msg.split("or")
        txt = f"React with ✅ for {op1} or ❎ for {op2}"
    except:
        await channel.send("correct syntax: [choice1] or [choice2]")
        return
    
    embed = discord.Embed(title="Poll", description = txt, colour = discord.Colour.red())
    message_ = await channel.send(embed=embed)
    await message_.add_reaction("✅")
    await message_.add_reaction("❎")

@bot.command()
async def meme(ctx):
    channel = ctx.channel
    subreddit = await reddit.subreddit("ProgrammerHumor")
    random_submission = await subreddit.random()
    name = random_submission.title
    url = random_submission.url
    em = discord.Embed(title = name, url = f"http://reddit.com{random_submission.permalink}")
    em.set_image(url = url)
    await channel.send(embed=em)

@bot.command()
async def kanye(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.kanye.rest/") as response:
            data = await response.json()
            await ctx.channel.send(data['quote'])

@bot.command(aliases=["r", "reminder", "remind"])
async def remindme(ctx, time, *, msg):
    sleep_time = await helper.convert(time)
    if sleep_time == -1:
        await ctx.channel.send(f"Invalid syntax.")
    else:
        await ctx.channel.send(f"{ctx.author.mention} you will be reminded in {time}")
        await asyncio.sleep(sleep_time)
        await ctx.channel.send(f"{ctx.author.mention}: {msg}")

@bot.command()
async def weather(ctx,*,msg="default"):
    author = ctx.author.id
    message = await Weather.checkWeather(author,msg)
    await ctx.channel.send(message)

@bot.command()
async def setcity(ctx,*,msg):
    if (await Weather.set_city(ctx, msg)):
        await ctx.channel.send(f"Successfully set city to {msg}")
    else: 
        await ctx.channel.send(f"Error with setting city to {msg}")

@bot.command()
async def ping(ctx):
    await ctx.channel.send("pong")

@bot.command(aliases=["shorten"])
async def short(ctx,link="False"):
    if (link == False):
        await ctx.channel.send("Please enter a valid url")
    else:
        await ctx.channel.send(await WebsiteAPI.shorten(link))
    
@bot.command()
async def python(ctx,*,code):
    if code[:3] == "```":
        code = code.strip("```python")
        code = code.strip("```")
    results = await helper.compile("python3", "4", code)
    await ctx.channel.send(f"```{results}```")

@bot.command()
async def java(ctx,*,code):
    if code[:3] == "```":
        code = code.strip("```java")
        code = code.strip("```")
    results = await helper.compile("java", "1", code)
    await ctx.channel.send(f"```{results}```")


# -----------------------------------------------------------------------------------------
#                               Moderation stuffs
# -----------------------------------------------------------------------------------------
async def is_authorized(ctx):
    if ctx.author.guild_permissions.kick_members:
        return True
    if await WebsiteAPI.is_bot_admin(ctx.author.id):
        return True
    await ctx.send("You do not have the required permissions or roles to use this command.")
    return False

@bot.command(aliases=["c"])
async def clear(ctx, amount:int=2):
    if not await is_authorized(ctx):
        return
    await ctx.channel.purge(limit = amount)

@bot.command(aliases=["b"])
async def ban(ctx, member:discord.Member,*,reason="No reason provided"):
    if not await is_authorized(ctx):
        return
    await ctx.send(f"{member.name} has been banned from the server for: {reason}")
    await member.send(f"You have been banned from the server for reason: {reason}")
    await member.ban(reason=reason)

@bot.command(aliases=['ub'])
async def unban(ctx,*,member):
    if not await is_authorized(ctx):
        return
    banned_users = await ctx.guild.bans()
    member_name, member_disc = member.split("#")
    for banned_user in banned_users:
        user = banned_user.user
        if (user.name, user.discriminator) == (member_name, member_disc):
            await ctx.guild.unban(user)
            await ctx.send(f"{member_name} has been unbanned")
            return
    await ctx.send(f"{member} was not found.")

@bot.command(aliases=["k"])
async def kick(ctx, member : discord.Member, *, reason="No reason provided"):
    if not await is_authorized(ctx):
        return
    await ctx.send(f"{member.name} has been kicked from the server for: {reason}")
    await member.send(f"You have been kicked from the server for reason: {reason}")
    await member.kick(reason=reason)

@bot.command(aliases=["m"])
async def mute(ctx, member: discord.Member):
    if not await is_authorized(ctx):
        return
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(mutedRole)
    await member.send(f" you have mutedd from: - {ctx.guild.name}")
    embed = discord.Embed(title="unmute", description=f" muted-{member.mention}",colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)

@bot.command(aliases=["um"])
async def unmute(ctx, member: discord.Member):
    if not await is_authorized(ctx):
        return
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(mutedRole)
    await member.send(f" you have unmutedd from: - {ctx.guild.name}")
    embed = discord.Embed(title="unmute", description=f" unmuted-{member.mention}",colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)

@bot.command(aliases=["user", "info"])
async def whois(ctx, member:discord.Member):
    if not await is_authorized(ctx):
        return
    embed = discord.Embed(title = member.name, description = member.mention, color = discord.Colour.red())
    embed.add_field(name = "ID", value = member.id, inline = True)
    embed.add_field(name="Top role", value = member.top_role)
    embed.set_thumbnail(url = member.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.name}")

    await ctx.send(embed=embed)

@bot.command()
async def set(ctx,setting, channel: discord.TextChannel):
    if not await is_authorized(ctx):
        return
    data = {
        "_id": ctx.guild.id,
        "type": "server"
    }
    if (setting == "join"):
        data['joinChannel'] = channel.id
    elif (setting == "leave"):
        data['leaveChannel'] = channel.id
    elif (setting == "rules"):
        data['rulesChannel'] = channel.id
    elif (setting == "announce"):
        data['announceChannel'] = channel.id
    if (await WebsiteAPI.add_data(data)):
        await ctx.channel.send(f"Set {setting} channel to {channel.mention}")
    else:
        await ctx.channel.send("Failure")

# -----------------------------------------------------------------------------------------
#                               Owner commands
# -----------------------------------------------------------------------------------------


def job_error_listener(event):
    job = scheduler.get_job(event.job_id)
    if job:  # Check if job is not None
        logging.error(f"Job {job.id} failed to execute: {event.exception}")
    else:
        logging.error(f"Job with ID {event.job_id} failed to execute, but job could not be found.")

scheduler.add_listener(job_error_listener, apscheduler.events.EVENT_JOB_ERROR)

@bot.command()
async def schedule(ctx, days: str, hour: int, minute: int, *, message: str):
    if not (await WebsiteAPI.is_bot_admin(ctx.author.id)):
        await ctx.send("You are not authorized to use this command.")
        return

    days = days.lower().replace('monday', 'mon').replace('tuesday', 'tue') \
        .replace('wednesday', 'wed').replace('thursday', 'thu') \
        .replace('friday', 'fri').replace('saturday', 'sat').replace('sunday', 'sun')
    scheduler.add_job(scheduled_message,CronTrigger(day_of_week=days, hour=hour, minute=minute),args=[ctx.channel.id, message])
    await ctx.send(f"Message scheduled in this channel on {days} at {hour:02d}:{minute:02d}.")

@bot.command()
async def list_schedules(ctx):
    if not (await WebsiteAPI.is_bot_admin(ctx.author.id)):
        await ctx.send("You are not authorized to use this command.")
        return
    
    jobs = scheduler.get_jobs()
    if jobs:
        response = "**Scheduled Messages:**\n"
        for job in jobs:
            print(dir(job))
            response += f"ID: `{job.id}` - Next Run: {getattr(job, 'next_run_time', 'Unavailable')}\n"
        await ctx.send(response)
    else:
        await ctx.send("No scheduled messages found.")

@bot.command()
async def delete_schedule(ctx, job_id: str):
    if not (await WebsiteAPI.is_bot_admin(ctx.author.id)):
        await ctx.send("You are not authorized to use this command.")
        return
    
    job = scheduler.get_job(job_id)
    if job:
        job.remove()
        await ctx.send(f"Deleted scheduled message with ID `{job_id}`.")
    else:
        await ctx.send(f"No scheduled message found with ID `{job_id}`.")

@bot.command()
async def restart(ctx):
    if (await WebsiteAPI.is_bot_admin(ctx.author.id)):
        await ctx.channel.send("Restarting bot")
        os.execv(sys.executable, ['python'] + [sys.argv[0]])
    else:
        await ctx.channel.send("You do not have valid permissions for this")    

@bot.command()
async def update(ctx):
    if (await WebsiteAPI.is_bot_admin(ctx.author.id)):
        msg = g.pull()
        await ctx.channel.send(msg)
    else:
        await ctx.channel.send("You do not have valid permissions for this") 

@bot.event
async def on_member_remove(member):
    data = await WebsiteAPI.get_data(member.guild.id, "server")
    if ("leaveChannel" in data):
        c = bot.get_channel(int(data['leaveChannel']))
    await c.send(f"**{member}** has left the server")

@bot.event
async def on_member_join(member):
    data = await WebsiteAPI.get_data(member.guild.id, "server")
    embed = discord.Embed(title="Member Joined", description=f"{member.mention}, Welcome to {member.guild.name}. We hope that your time with us is a happy one!")
    if ("rulesChannel" in data):
        rules = bot.get_channel(int(data['rulesChannel']))
        embed.add_field(name="Please check out the Rules Channel!", value=rules.mention, inline=False)
    if ("announceChannel" in data):
        announce = bot.get_channel(int(data['announceChannel']))
        embed.add_field(name="Latest announcements are made here!", value=announce.mention, inline=False)
    if ("joinChannel" in data):
        c = bot.get_channel(int(data['joinChannel']))
    else:
        c = discord.utils.get(member.guild.channels, name="general")
    await c.send(embed=embed)

@bot.event
async def on_message_edit(message_before, msg):
    if msg.channel.id == announce_id:
        data = {
        "_id": msg.id,
        "message": msg.content,
        "type": "announcement",
        "author": msg.author.name
        }
        await WebsiteAPI.add_data(data)

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't do that.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter all the required args.")
    elif isinstance(error,commands.CommandNotFound):
        await ctx.send("Command not found, please use !help to see a list of commands")
    else:
        raise error

async def scheduled_message(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        message_ = await channel.send(message)
        await message_.add_reaction("✅")
        await message_.add_reaction("❎")
    else:
        print(f"Channel {channel_id} not found.")


bot.run(getenv("TOKEN"))
