import asyncio
import platform
import re

import discord
from discord.ext import commands
import yt_dlp as youtube_dl

from music import LinkedList

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4
    'fixup': 'warn'  # This flag may help with fixing incomplete files
}

ffmpeg_options = {
    'options': '-vn'
}
music_list = LinkedList()

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_path = "ffmpeg.exe"
if platform.system() != "Windows":
    ffmpeg_path = "/usr/bin/ffmpeg"


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        ytdl.cache.remove()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@bot.command(name='join_bot', help='Tells the bot to join the voice channel | order: !join_bot')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave_bot', help='To make the bot leave the voice channel | order: !leave_bot')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='insert_music', help='insert music | order: !insert_music {youtube_music_url}')
async def insert_music(ctx, url):
    await ctx.send("正在幫你新增歌曲到歌單中....")
    filename = await YTDLSource.from_url(url, loop=bot.loop)
    music_list.append(filename)
    await ctx.send(f"點歌點好囉\n歌單:\n" + "\n".join(
        [f"第{index + 1}首歌: {song}" for index, song in enumerate(music_list.list_all())]
    ))


@bot.command(name='music_list', help='music list | order: !music_list')
async def list_music(ctx):
    song_list = music_list.list_all()
    if song_list:
        await ctx.send("歌單:\n" + "\n".join([f"第{index + 1}首歌: {song}" for index, song in enumerate(song_list)]))
    else:
        await ctx.send("歌單目前是空的")


@bot.command(name='remove_music', help='remove | order: !remove_music {music_name}')
async def remove_music(ctx, music):
    if music_list.remove(music):
        await ctx.send(f"已移除: {music}")
    else:
        await ctx.send("未找到該歌曲")


@bot.command(name='play_music', help='To play all music Hi Yaku | order: !play_music ')
async def music_li(ctx):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            for song in music_list.list_all():
                voice_channel.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=song))
                await ctx.send(f'**Now playing:** {song}')

                while voice_channel.is_playing():
                    await asyncio.sleep(2)
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='next_music', help='Play the next song | order: !next_music')
async def next_music(ctx):
    voice_channel = ctx.message.guild.voice_client
    if voice_channel.is_playing():
        voice_channel.stop()

    if not voice_channel or not voice_channel.is_connected():
        await ctx.send("The bot is not connected to a voice channel.")
        return

    song = music_list.get_next_song()
    if song:
        voice_channel.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=song))
        await ctx.send(f"**Now playing next song:** {song}")
    else:
        await ctx.send("No more songs in the queue.")


@bot.command(name='previous_music', help='Play the previous song | order: !previous_music')
async def previous_music(ctx):
    voice_channel = ctx.message.guild.voice_client
    if voice_channel.is_playing():
        voice_channel.stop()
    if not voice_channel or not voice_channel.is_connected():
        await ctx.send("The bot is not connected to a voice channel.")
        return

    song = music_list.get_previous_song()
    if song:
        voice_channel.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=song))
        await ctx.send(f"**Now playing previous song:** {song}")
    else:
        await ctx.send("No previous songs in the queue.")


@bot.event
async def on_ready():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if str(channel) == "general":
                await channel.send('Bot Activated..')
                await channel.send(file=discord.File('add_gif_file_name_here.png'))
        print('Active in {}\n Member Count : {}'.format(guild.name, guild.member_count))


if __name__ == "__main__":
    bot.run("your_api_key")
