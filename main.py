import discord
from discord.ext import commands
import logging

from dotenv import load_dotenv
import os
import mysql.connector
from datetime import datetime ,timedelta , timezone
tz = timezone(timedelta(hours=7))


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intent = discord.Intents.default()
intent.members = True
intent.message_content = True

connect = mysql.connector.connect(
    host=os.getenv('HOST'),
    user=os.getenv('USER'),
    password=os.getenv('PASSWORD'),
    database=os.getenv('DATABASE'),
    autocommit = True
)
cursor = connect.cursor()

queues = {}

def check_queue(ctx,id):
    if queues[id]:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        voice.play(source, after=lambda x=None : check_queue(ctx, ctx.message.guild.id))


bot = commands.Bot(command_prefix='*', intents=intent)

#-----------------------------------------------(EVENT)------------------------------------------------------------

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("Sword Art Online!"))
    print("----------------------------------------------")
    print(f"Bot {bot.user.name} has connected to Discord!")
    print("----------------------------------------------")

@bot.event
async def on_disconnect():
        cursor.close()
        connect.close()


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1398605337850024019)
    sql = "INSERT INTO user (user_id, username) VALUES (%s, %s)"
    val = (member.id,member.name)
    cursor.execute(sql, val)
    dis_embed = discord.Embed(title=f"Welcome to {member.guild.name} server!",
                          description=f"{member.mention} has joined the server!",
                          color=discord.Color.purple(),
                          timestamp=datetime.now()
                          )
    dis_embed.set_image(url="https://saoub.fanadata.com/assets/characters/artwork/character_171_4.png")

    await channel.send(embed=dis_embed)
    await channel.send(f"{member.mention} has joined the server!")

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(1398605337850024019)
    sql = "DELETE FROM discord_bot.user WHERE user_id = %s"
    val = (member.id,)
    cursor.execute(sql, val)
    await channel.send(f"{member.mention} has left the server!")

@bot.event
async def on_message_edit(before,after):
    channel = bot.get_channel(1398605337850024019)
    await channel.send(
        f"{before.author.mention} has changed message\n"
        f"Before : {before.content}\n"
        f"After : {after.content}"
    )
    sql = "INSERT INTO message_log (message_id, username, action, content_message, message_after, timestamp, original_timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (before.id, before.author.name, "Edit Message", before.content, after.content, datetime.now(),before.created_at.astimezone(tz))
    cursor.execute(sql, val)

@bot.event
async def on_message_delete(delete):
    channel = bot.get_channel(1398605337850024019)
    sql = "INSERT INTO message_log (message_id, username, action, content_message, timestamp) VALUES (%s, %s, %s, %s, %s)"
    val = (delete.id,delete.author.name,"Delete Message",delete.content,datetime.now())
    cursor.execute(sql, val)
    await channel.send(f"{delete.author.mention} has deleted the message : {delete.content}")

#-----------------------------------------------(COMMAND)------------------------------------------------------------

@bot.command()
async def about(ctx):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, timestamp) VALUES (%s, %s, %s, %s)"
    val = (ctx.message.author.name, "about", channel, datetime.now())
    cursor.execute(sql, val)
    dis_embed = discord.Embed(title=f"About me!",
                              description=f"Hi! {ctx.author.mention} Here The Command List!",
                              color=discord.Color.purple(),
                              timestamp=datetime.now()
                              )

    dis_embed.set_author(name="DevilSpotGS",url="https://www.youtube.com/@DevilSpotGS",icon_url="https://scontent.fkdt2-1.fna.fbcdn.net/v/t39.30808-6/491454765_9541765055944129_2766076166498059368_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=a5f93a&_nc_ohc=Ltr0w2DT3e8Q7kNvwEJy_B4&_nc_oc=Adl4VjvmZw6pcTUvnVESgPbX7sPdA8Oiiq6Q0VJzTo4gdajGElFHXyf85w9ZRItlJFc&_nc_zt=23&_nc_ht=scontent.fkdt2-1.fna&_nc_gid=H5po0tFb0nuzwysZAJRkbQ&oh=00_Afdb1z-eibAqzITp3pnlOwiboFy7JzeEb8GNn-lpNtuGvw&oe=68E94B61")
    dis_embed.set_thumbnail(url="https://scontent.fkdt2-1.fna.fbcdn.net/v/t39.30808-6/488774902_9454844381302864_5770821389214987748_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=a5f93a&_nc_ohc=OILsJXtLRd4Q7kNvwHwi-Wp&_nc_oc=Adkd5XhIJNiDdbfFdhCbYVt892Az3BOENY07JW4zsGFsnozMu3yCOEk_TCaX1SKl01s&_nc_zt=23&_nc_ht=scontent.fkdt2-1.fna&_nc_gid=fm_cIxtoXOOx_kCYTM_7GA&oh=00_AfdmZr7QrxjqTmi_NyPP9Llq63xb_EUjQhLsOtphQB57sw&oe=68E96CD7")
    dis_embed.set_image(url="https://scontent.fkdt2-1.fna.fbcdn.net/v/t39.30808-6/492972717_9614419915345309_5552633255201502682_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=cc71e4&_nc_ohc=zUgPQKz-mGoQ7kNvwFaW9ek&_nc_oc=AdnTgXIKQchJKDCABGvo2b7unK65KUIZLskGDZoMpLL2vKpXAZgkKg4SAsqyGCMkBgs&_nc_zt=23&_nc_ht=scontent.fkdt2-1.fna&_nc_gid=5KR6cH7KnjuUsqgl3ln5ew&oh=00_AfcWmWnSKTUPtqxvEL3u6TfyY5DMJ7V4GFfmZ6UU_-SPPg&oe=68E94C8C")
    dis_embed.set_footer(text="Stay with Determination!",icon_url="https://scontent.fkdt2-1.fna.fbcdn.net/v/t39.30808-6/487552476_9426641564123146_2217554778652060851_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=a5f93a&_nc_ohc=QinRTkTs2oEQ7kNvwEP1to_&_nc_oc=AdlwCQqYlgumo9KStKeQo4Nj6RpSX7BeycuCyHL9KHPt4aeC0haBnv66a1H1ZQwfXaI&_nc_zt=23&_nc_ht=scontent.fkdt2-1.fna&_nc_gid=XmG5sVVZD4hUQ1GKw6gg8g&oh=00_AffnNGCoQOWUj557BcKmahTreQ3Z2S9i82igGT8NI5Ll-g&oe=68E96CB6")

    dis_embed.add_field(name="*test",value="- send message",inline=True)
    dis_embed.add_field(name="*dm", value="- dm a message to you", inline=False)
    dis_embed.add_field(name="*reply", value="- reply your message", inline=False)
    dis_embed.add_field(name="*poll", value="- poll a question", inline=False)
    dis_embed.add_field(name="*join", value="- join in voice channel", inline=False)
    dis_embed.add_field(name="*leave", value="- leave voice channel", inline=False)
    dis_embed.add_field(name="*play song", value="- play a song", inline=False)
    dis_embed.add_field(name="*queue song", value="- add a song into Queue", inline=False)
    dis_embed.add_field(name="*pause", value="- pause a song", inline=False)
    dis_embed.add_field(name="*resume", value="- Resume a song", inline=False)
    dis_embed.add_field(name="stop", value="- Stop a song", inline=False)
    await ctx.send(embed=dis_embed)

@bot.command()
async def song(ctx):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, timestamp) VALUES (%s, %s, %s, %s)"
    val = (ctx.message.author.name, "song_list", channel, datetime.now())
    cursor.execute(sql, val)
    dis_embed = discord.Embed(title=f"Song list!",
                              description=f"Hi! {ctx.author.mention} Here The Song List!",
                              color=discord.Color.blue(),
                              timestamp=datetime.now()
                              )

    dis_embed.add_field(name="Song name:",value="Asgore , Crossingfield ,Last Resort")
    await ctx.send(embed=dis_embed)

@bot.command()
async def test(ctx,*,arg):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, content_message, timestamp) VALUES (%s, %s, %s, %s, %s)"
    val = (ctx.message.author.name, "test", channel, arg, datetime.now())
    cursor.execute(sql, val)
    await ctx.send(f"{ctx.author.mention} said {arg}")

@bot.command()
async def dm(ctx,*,arg):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, content_message, timestamp) VALUES (%s, %s, %s, %s, %s)"
    val = (ctx.message.author.name, "dm", channel, arg, datetime.now())
    cursor.execute(sql, val)
    await ctx.author.send(f"Hi {ctx.author.mention} ,You said :{arg}")

@bot.command()
async def reply(ctx,*,arg):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, content_message, timestamp) VALUES (%s, %s, %s, %s, %s)"
    val = (ctx.message.author.name, "reply", channel, arg, datetime.now())
    cursor.execute(sql, val)
    await ctx.reply(f"Reply to this message : {arg}")

@bot.command()
async def poll(ctx,*,question):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, content_message, timestamp) VALUES (%s, %s, %s, %s, %s)"
    val = (ctx.message.author.name, "poll", channel, question, datetime.now())
    cursor.execute(sql, val)
    embed = discord.Embed(title="Polling", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("😭")
    await poll_message.add_reaction("🧍")


@bot.command()
async def join(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice is None:
        channel = ctx.author.voice.channel
        sql = "INSERT INTO voice_log (username, channel_id, command, timestamp) VALUES (%s, %s, %s, %s)"
        val = (ctx.author.name, channel.id, "Join", datetime.now())
        cursor.execute(sql, val)
        await channel.connect()
        await ctx.send(f"{bot.user.mention} has joined the {channel.mention}")
    else:
        await ctx.send(f"You are not connected to a voice channel")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        channel = ctx.author.voice.channel
        await ctx.voice_client.disconnect()
        await ctx.send(f"{bot.user.mention} has left the voice channel")
        sql = "INSERT INTO voice_log (username, channel_id, command, timestamp) VALUES (%s, %s, %s, %s)"
        val = (ctx.author.name, channel.id, "Leave", datetime.now())
        cursor.execute(sql, val)
    elif ctx.author.voice :
        await ctx.send(f"Bot are not connected to a voice channel")
    else:
        await ctx.send(f"You are not connected to a voice channel")

#--------------------------------------------(Command-Song)----------------------------------------------------------

@bot.command()
async def play(ctx,*,arg):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, content_message, timestamp) VALUES (%s, %s, %s, %s, %s)"
    val = (ctx.message.author.name, "play", channel, arg, datetime.now())
    cursor.execute(sql, val)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    song = arg + ".wav"
    source = discord.FFmpegPCMAudio(song)
    voice.play(source , after=lambda x=None : check_queue(ctx,ctx.message.guild.id))
    await ctx.send(f"Now playing {arg}")

@bot.command()
async def queue(ctx,*,arg):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, content_message, timestamp) VALUES (%s, %s, %s, %s, %s)"
    val = (ctx.message.author.name, "queue", channel, arg, datetime.now())
    cursor.execute(sql, val)
    song = arg + ".wav"
    source = discord.FFmpegPCMAudio(song)

    guild_id = ctx.message.guild.id

    if guild_id in queues:
        queues[guild_id].append(source)

    else:
        queues[guild_id] = [source]

    await ctx.send(f"Added {arg} to the queue")

@bot.command()
async def pause(ctx):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, timestamp) VALUES (%s, %s, %s, %s)"
    val = (ctx.message.author.name, "pause", channel, datetime.now())
    cursor.execute(sql, val)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("There isn't have any songs play now")

@bot.command()
async def resume(ctx):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, timestamp) VALUES (%s, %s, %s, %s)"
    val = (ctx.message.author.name, "resume", channel, datetime.now())
    cursor.execute(sql, val)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The voice client is not connected to a voice channel")

@bot.command()
async def stop(ctx):
    channel = ctx.message.channel.id
    sql = "INSERT INTO command_log (username, command, channel_id, timestamp)VALUES (%s, %s, %s, %s)"
    val = (ctx.message.author.name, "stop", channel, datetime.now())
    cursor.execute(sql, val)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


bot.run(TOKEN,log_handler=handler,log_level=logging.DEBUG)