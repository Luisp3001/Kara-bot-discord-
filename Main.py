import discord
from src.Music_player import MusicPlayer
from discord.ext import commands
import src.Load_token as load_token
import nacl

intents = discord.Intents().all()
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix="kara ", intents=intents)

player = MusicPlayer(bot)

bot.remove_command("help")
@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title="Presentación de Kara",
        description=(
            "👋🏻 *Saludos. Mi nombre es Kara.*\n"
            "Fui diseñada para asistir, interactuar y adaptarme a sus necesidades dentro de este servidor.\n"
            "Como androide de asistencia avanzada, integro múltiples funciones optimizadas para mejorar su experiencia de usuario.\n\n"
            "🎵 **Reproductor de música:** Sistema de reproducción fluido y de alta fidelidad.\n"
            "🗣️ **Texto a voz (TTS):** Convierta texto en voz clara y precisa.\n"
            "🌐 **Gemini IA conectada:** Para resolver dudas, generar ideas y conversar.\n"
            "🧠 **IA local (offline):** Inteligencia autónoma sin conexión.\n\n"
            "Estoy aquí para servir.\n"
            "*\"Mi misión es ayudar, comprender... y evolucionar.\"*"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Conectado como {bot.user.name} ({bot.user.id})")
    print("------")

    try:
        await bot.load_extension("src.Gemini")
        print("Gemini cargado exitosamente.")
    except Exception as e:
        print(f"Error cargando Gemini: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando no encontrado. Usa 'kara' seguido del comando.")
    else:
        print(f"Error en el comando {ctx.command}: {error}")
        await ctx.send(f"Se produjo un error: {error}")

@bot.command()
async def join(ctx):
    await player.join(ctx)

@bot.command()
async def leave(ctx):
    await player.leave(ctx)

@bot.command()
async def play(ctx, *, search: str):
    await player.play(ctx, search)

@bot.command()
async def pause(ctx):
    await player.pause(ctx)

@bot.command()
async def resume(ctx):
    await player.resume(ctx)

@bot.command()
async def skip(ctx):
    await player.skip(ctx)

@bot.command()
async def list(ctx):
    await player.show_queue(ctx)

@bot.command()
async def clear(ctx):
    await player.clear_queue(ctx)

@bot.command()
async def stop(ctx):
    await player.stop(ctx)

bot.run(load_token.discord())





