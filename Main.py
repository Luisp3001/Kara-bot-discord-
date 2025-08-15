import discord
from src.Music_player import MusicPlayer
from discord.ext import commands
from src.load_tkn import load_token
from src.db_files import permissions as perm
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
            "- 🎵 **Reproductor de música:** Sistema de reproducción fluido y de alta fidelidad.\n"
            "  - **Como funciona: ** usa el prefijo 'kara' seguido del comando, ejemplo: `kara play <nombre_canción>`\n"
            "  - **Comandos disponibles: ** `play, pause, resume, stop, skip, shuffle, list, remove`.\n"         
            "- 🗣️ **Texto a voz (TTS):** Convierta texto en voz clara y precisa.\n"
            "  - **Como funciona: ** usa el prefijo 'kara' seguido del comando, ejemplo: `kara tts <mensaje>`\n"
            "- 🌐 **Gemini IA conectada:** Para resolver dudas, generar ideas y conversar.\n"
            "  - **Como funciona: ** usa el prefijo 'kara' seguido del comando, ejemplo: `kara gemini <prompt>`\n"
            "- 🧠 **IA local (offline):** Inteligencia autónoma sin conexión.\n\n"
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
async def Sp(ctx, user: discord.User, role: int):
    admin_role = perm.get_permission(ctx.author.id)
    
    if not admin_role or admin_role < 3:
        await ctx.send("No tienes permisos para asignar roles.")
        return
    
    if user.id == 748048975000633384:
        await ctx.send("No puedes cambiar los permisos del propietario del bot.")
        return
    
    if role not in [1, 2, 3]:
        await ctx.send("El rol debe ser 1 (usuario), 2 (moderador) o 3 (admin).")
        return
    
    
    perm.set_permission(user.id, role)
    out = (f"Permisos actualizados: Usuario {user} ahora tiene permisos de nivel {role} ")
    await ctx.send(out + "(usuario)" if role == 1 else out + "(moderador)" if role == 2 else out + "(admin)")

@bot.command()
async def Qp(ctx, user: discord.User):
    role = perm.get_permission(user.id)
    if perm.get_permission(ctx.author.id) != 3:
        await ctx.send("No tienes permisos para consultar los roles de otros usuarios.")
        return
    
    if role is not None:
        out = (f"El usuario {user} tiene permisos de nivel {role} ")
        await ctx.send(out + "(usuario)" if role == 1 else out + "(moderador)" if role == 2 else out + "(admin)")
    else:
        await ctx.send(f"No se encontraron permisos para el usuario {user}.")

@bot.command()
async def leave(ctx):
    await player.leave(ctx)

@bot.command()
async def play(ctx, *, search: str):
    if perm.get_permission(ctx.author.id) is None:
        await ctx.send("No tienes permisos para hacer uso del bot.")
        return
    else:
        await player.play(ctx, search)

@bot.command()
async def pause(ctx):
    if perm.get_permission(ctx.author.id) is None:
        await ctx.send("No tienes permisos para hacer uso del bot.")
        return
    elif perm.get_permission(ctx.author.id) == 1:
        await ctx.send("No tienes permisos para pausar la música.")
        return
    await player.pause(ctx)

@bot.command()
async def resume(ctx):
    if perm.get_permission(ctx.author.id) is None:
        await ctx.send("No tienes permisos para hacer uso del bot.")
        return
    elif perm.get_permission(ctx.author.id) == 1:
        await ctx.send("No tienes permisos para reanudar la música.")
        return
    await player.resume(ctx)

@bot.command()
async def skip(ctx):
    if perm.get_permission(ctx.author.id) is None:
        await ctx.send("No tienes permisos para hacer uso del bot.")
        return
    elif perm.get_permission(ctx.author.id) == 1:
        await ctx.send("No tienes permisos para saltar la música.")
        return
    await player.skip(ctx)

@bot.command()
async def list(ctx):
    await player.show_queue(ctx)

@bot.command()
async def clear(ctx):
    if perm.get_permission(ctx.author.id) is None:
        await ctx.send("No tienes permisos para hacer uso del bot.")
        return
    elif perm.get_permission(ctx.author.id) == 1:
        await ctx.send("No tienes permisos para limpiar la cola.")
        return
    await player.clear_queue(ctx)

@bot.command()
async def stop(ctx):
    if perm.get_permission(ctx.author.id) is None:
        await ctx.send("No tienes permisos para hacer uso del bot.")
        return
    elif perm.get_permission(ctx.author.id) == 1:
        await ctx.send("No tienes permisos para detener la música.")
        return
    await player.stop(ctx)

@bot.command()
async def remove(ctx, index: int):
    if perm.get_permission(ctx.author.id) is None:
        await ctx.send("No tienes permisos para hacer uso del bot.")
        return
    elif perm.get_permission(ctx.author.id) == 1:
        await ctx.send("No tienes permisos para eliminar canciones de la cola.")
        return
    await player.remove(ctx, index)

@bot.command()
async def shuffle(ctx):
    await player.shuffle(ctx)


bot.run(load_token.discord())





