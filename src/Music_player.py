import discord
import random
import asyncio
from discord.ext import commands
from discord import FFmpegOpusAudio
import yt_dlp as yt 

ytdl_opts = { 
    'format': 'bestaudio/best',
    'default_search': 'ytsearch',
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
        'preferredquality': '192',
    }]
}
ytdl = yt.YoutubeDL(ytdl_opts)

class MusicPlayer:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues = {}

    def get_queue(self, guild_id):
        return self.queues.setdefault(guild_id, [])
    
    async def join(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
                print(f"Conectada a {channel}")
            else:
                await ctx.send("Necesitas estar en un canal de voz para que me una.")
        else:
            await ctx.send("Ya estoy en un canal de voz.")
        
    async def leave(self, ctx):
        voice = ctx.guild.voice_client
        if voice:
            await voice.disconnect()
            self.queues.pop(ctx.guild.id, None)
            await ctx.send("Me he desconectado del canal de voz.")
        else:
            await ctx.send("No estoy conectada a ningún canal de voz.")

    async def play(self, ctx, search: str):
        voice = ctx.guild.voice_client
        if not voice:
            await ctx.send("No estoy en un canal de voz. Usa 'join' para unirte.")
            return

        try: 
            loop = asyncio.get_event_loop()
            if search.startswith("https://") or search.startswith("www"):
                info = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
            else:
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{search}", download=False))
                info = data["entries"][0]
        except Exception as e:
            await ctx.send(f"Hubo un error al buscar la canción :( {e}")
            return

        url = info['url']
        title = info['title']
        webpage = info.get('webpage_url', 'No URL')

        queue = self.get_queue(ctx.guild.id)

        if voice.is_playing() or voice.is_paused():
            queue.append(title)
            embed=discord.Embed(
                color=discord.Colour.random(),
                title="",
                description=""
            )
            embed.set_author(name=self.bot.user.name, icon_url=str(self.bot.user.avatar))
            embed.add_field(name="**Añadida a la lista**",value=f"[{info['title']}]({info['webpage_url']})",inline=True)
            embed.set_thumbnail(url=f"https://avatar.glue-bot.xyz/youtube-thumbnail/q?url={info['webpage_url']}")
            embed.set_footer(text="Añadida por {}".format(ctx.message.author.name), icon_url=str(ctx.message.author.avatar))
            await ctx.send(embed=embed)
        else: 
            await self._start_playback(ctx, url, title, webpage)
    
    async def _start_playback(self, ctx, url, title, webpage):
        voice = ctx.guild.voice_client

        loop = asyncio.get_event_loop()
        source = await loop.run_in_executor(None, lambda: FFmpegOpusAudio(url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn"))    
        
        def after_play(error):
            fut = asyncio.run_coroutine_threadsafe(self._play_next(ctx), self.bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error al reproducir la siguiente canción: {e}")
        
        voice.play(source=source, after=after_play)
        
        embed=discord.Embed(
            color=discord.Colour.random(),
            title="",
            description=""
        )
        embed.set_author(name=self.bot.user.name, icon_url=str(self.bot.user.avatar))
        embed.add_field(name="**Reproduciendo**",value=f"[{title}]({webpage})",inline=True)
        embed.set_thumbnail(url=f"https://avatar.glue-bot.xyz/youtube-thumbnail/q?url={webpage}")
        embed.set_footer(text="Reproduciendo por {}".format(ctx.message.author.name), icon_url=str(ctx.message.author.avatar))
        await ctx.send(embed=embed)

    async def _play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if queue:
            next_song = queue.pop(0)
            try:
                if next_song.startswith(("https://")):
                    info = ytdl.extract_info(next_song, download=False)
                else:
                    info = ytdl.extract_info(f"ytsearch:{next_song}", download=False)['entries'][0]
                await self._start_playback(ctx, info['url'], info['title'], info.get('webpage_url', 'No URL'))
            except Exception as e:
                await ctx.send("Error al reproducir la siguiente canción. ❌")
                print(e)
        else:
            await ctx.send("La cola ha terminado. 🛑")

    async def pause(self, ctx):
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            voice.pause()
            await ctx.send("He pausado la canción. ⏸️")
        else:
            await ctx.send("No estoy reproduciendo nada.")
    
    async def resume(self, ctx):
        voice = ctx.guild.voice_client
        if voice and voice.is_paused():
            voice.resume()
            await ctx.send("He reanudado la canción. ▶️")
        else:
            await ctx.send("No estoy reproduciendo nada.")
    
    async def stop(self, ctx): 
        voice = ctx.guild.voice_client
        if voice and (voice.is_playing() or voice.is_paused()):
            voice.stop()
            await ctx.send("He detenido la reproducción. ⛔")
        else:
            await ctx.send("No estoy reproduciendo nada.")

    async def clear_queue(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if queue:
            queue.clear()
            await ctx.send("He limpiado la cola. 🗑️")
        else:
            await ctx.send("No hay canciones en la cola.")        

    async def skip(self, ctx):
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            voice.stop()
            await ctx.send("Saltando canción... ⏭️")
        else:
            await ctx.send("No hay música para saltar.")

    async def remove(self, ctx, index: int):
        queue = self.get_queue(ctx.guild.id)
        if queue and 0 < index <= len(queue):
            removed_song = queue.pop(index - 1)
            await ctx.send(f"Se ha eliminado la canción: {removed_song} ❌")
        else:
            await ctx.send("Índice inválido o cola vacía.")

    async def shuffle(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if queue:
            random.shuffle(queue)
            await ctx.send("He mezclado la cola. 🔀")
        else:
            await ctx.send("No hay canciones en la cola.")    

    async def show_queue(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if queue:
            embed=discord.Embed(
                    color=discord.Colour.random(),
                    title="Lista de reproduccion:",
                    description=""
                )
            embed.set_author(name=self.bot.user.name, icon_url=str(self.bot.user.avatar))
            counter = 1
            for songs in queue:
                embed.add_field(name="",value=f"{counter}-"+"".join(songs)+"\n",inline=False)
                counter+=1
            embed.set_footer(text="Solicitada por {}".format(ctx.message.author.name), icon_url=str(ctx.message.author.avatar))
            await ctx.send(embed=embed)
        else:
            await ctx.send("No hay canciones en la cola.")