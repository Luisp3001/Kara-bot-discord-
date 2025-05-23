import discord
import os
import asyncio
from discord.ext import commands
import google.generativeai as genai
import src.Load_token as load_token

class Gemini:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("Modelo Gemini cargado correctamente.")
        except Exception as e:
            print(f"Error al cargar el modelo Gemini: {e}")
            self.model = None

    async def generate_response(self, prompt: str) -> str:
        if self.model is None:
            return "Lo siento, el modelo Gemini no está disponible en este momento."
        try:
            response =  await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text
        except Exception as e:
            print(f"Ocurrio un error al comunicarse con los servicios de gemini: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."
    
class GeminiCog(commands.Cog):
    def __init__(self, bot: commands.Bot, gemini_api_key: str):
        self.bot = bot
        self.gemini_service = Gemini(gemini_api_key)
        print("Gemini service initialized.")
        
    @commands.command()
    async def gemini(self, ctx, *, prompt: str):
        if not prompt:
            await ctx.send("Por favor, proporciona un prompt para Gemini.")
            return
            
        async with ctx.typing():
            response_text = await self.gemini_service.generate_response(prompt)
            if len(response_text) > 2000:
                parts = [response_text[i:i+2000] for i in range(0, len(response_text), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                await ctx.send(response_text)

    @commands.command()
    async def gemini_status(self, ctx: commands.Context):
        if self.gemini_service.model is not None:
            await ctx.send("El modelo Gemini está disponible y listo para usar.")
        else:
            await ctx.send("El modelo Gemini no está disponible en este momento.")

async def setup(bot: commands.Bot):
    gemini_api_key = load_token.gemini()
    if not gemini_api_key:
        print("WARNING: No se encontró la clave de API de Gemini.")
        return
    await bot.add_cog(GeminiCog(bot, gemini_api_key))