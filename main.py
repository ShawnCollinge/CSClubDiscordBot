import discord, random, asyncpraw, aiohttp, asyncio, helper, Weather, WebsiteAPI
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
load_dotenv()

reddit = asyncpraw.Reddit(client_id = getenv("REDDIT_CLIENT_ID"),
                    client_secret = getenv("REDDIT_CLIENT_SECRET"),
                    user_agent = getenv("REDDIT_USER_AGENT"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
long_homework = ["individual assignment", "long homework"]
already_sent = {"long_homework": False, "noice": False}

@bot.event
async def on_message(msg):
    if (msg.author.bot):
        return
    global already_sent
    if "lol" in msg.content:
        if (random.randint(0,10) == 2):
            await msg.channel.send("https://c.tenor.com/ASGuOCPGrKEAAAAd/kekw-kek.gif")
    if "noice" == msg.content:
        if not already_sent["noice"]:
            await msg.channel.send("https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/thematedkid/phpPlfUuy.gif")
            already_sent["noice"] = True
            await asyncio.sleep(60)
            already_sent["noice"] = False
    for word in long_homework:
        if word in msg.content:
            if not already_sent["long_homework"]:
                homework_channel = bot.get_channel(977627353247268884)
                await msg.channel.send(f"Remember to read the rules in {homework_channel.mention} before talking about long homework assignments")
                already_sent["long_homework"] = True
                await asyncio.sleep(3600)
                already_sent["long_homework"] = False

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
    subreddit = await reddit.subreddit("ProgrammerHumor")
    random_submission = await subreddit.random()
    name = random_submission.title
    url = random_submission.url
    em = discord.Embed(title = name, url = f"http://reddit.com{random_submission.permalink}")
    em.set_image(url = url)
    await ctx.channel.send(embed=em)

@bot.command()
async def kanye(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.kanye.rest/") as response:
            data = await response.json()
            await ctx.channel.send(data['quote'])

@bot.command(aliases=["r", "reminder", "remind"])
async def remindme(ctx, time, *, msg):
    sleep_time = helper.convert(time)
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
    message = await Weather.set_city(ctx, msg)
    await ctx.channel.send(message)

@bot.command(aliases=["shorten"])
async def short(ctx,link="False"):
    if (link == False):
        await ctx.channel.send("Please enter a valid url")
    else:
        await ctx.channel.send(await WebsiteAPI.shorten(link))


# -----------------------------------------------------------------------------------------
#                               Moderation stuffs
# -----------------------------------------------------------------------------------------
@bot.command(aliases=["c"])
@commands.has_permissions(manage_messages = True)
async def clear(ctx, amount:int=2):
    await ctx.channel.purge(limit = amount)

@bot.command(aliases=["b"])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member:discord.Member,*,reason="No reason provided"):
    await ctx.send(f"{member.name} has been banned from the server for: {reason}")
    await member.send(f"You have been banned from the server for reason: {reason}")
    await member.ban(reason=reason)

@bot.command(aliases=['ub'])
@commands.has_permissions(ban_members=True)
async def unban(ctx,*,member):
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
@commands.has_permissions(kick_members = True)
async def kick(ctx, member : discord.Member, *, reason="No reason provided"):
    await ctx.send(f"{member.name} has been kicked from the server for: {reason}")
    await member.send(f"You have been kicked from the server for reason: {reason}")
    await member.kick(reason=reason)

@bot.command(aliases=["m"])
@commands.has_permissions(kick_members = True)
async def mute(ctx, member: discord.Member):
   mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
   await member.add_roles(mutedRole)
   await member.send(f" you have mutedd from: - {ctx.guild.name}")
   embed = discord.Embed(title="unmute", description=f" muted-{member.mention}",colour=discord.Colour.light_gray())
   await ctx.send(embed=embed)

@bot.command(aliases=["um"])
@commands.has_permissions(kick_members = True)
async def unmute(ctx, member: discord.Member):
   mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
   await member.remove_roles(mutedRole)
   await member.send(f" you have unmutedd from: - {ctx.guild.name}")
   embed = discord.Embed(title="unmute", description=f" unmuted-{member.mention}",colour=discord.Colour.light_gray())
   await ctx.send(embed=embed)

@bot.command(aliases=["user", "info"])
@commands.has_permissions(kick_members=True)
async def whois(ctx, member:discord.Member):
    embed = discord.Embed(title = member.name, description = member.mention, color = discord.Colour.red())
    embed.add_field(name = "ID", value = member.id, inline = True)
    embed.add_field(name="Top role", value = member.top_role)
    embed.set_thumbnail(url = member.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.name}")

    await ctx.send(embed=embed)

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

bot.run(getenv("TOKEN"))