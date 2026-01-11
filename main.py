
import discord
import os
import asyncio
from discord.ext import commands
from audio_source import SystemAudioSource

# Helper to get token
def get_token():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("DISCORD_TOKEN environment variable not set.")
        token = input("Please enter your Discord Bot Token: ").strip()
    return token

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

bot = MusicBot()

@bot.tree.command(name="musicplease", description="Join your voice channel and stream system audio")
async def music_please(interaction: discord.Interaction):
    # Check if user is in a voice channel
    if not interaction.user.voice:
        await interaction.response.send_message("You are not connected to a voice channel.", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    
    await interaction.response.defer()

    # Connect to voice channel
    if interaction.guild.voice_client:
        if interaction.guild.voice_client.channel != channel:
            await interaction.guild.voice_client.move_to(channel)
    else:
        await channel.connect()

    voice_client = interaction.guild.voice_client

    # Stop current audio if playing
    if voice_client.is_playing():
        voice_client.stop()

    # Create audio source and play
    try:
        source = SystemAudioSource()
        voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
        await interaction.followup.send(f"Joined {channel.name} and started streaming system audio! 🎵")
    except Exception as e:
        await interaction.followup.send(f"Error starting audio stream: {e}", ephemeral=True)
        print(f"Error: {e}")

@bot.tree.command(name="stop", description="Stop streaming and leave")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Stopped streaming and disconnected.", ephemeral=False)
    else:
        await interaction.response.send_message("I am not connected to a voice channel.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Synced slash commands for {bot.user}")

if __name__ == "__main__":
    try:
        token = get_token()
        bot.run(token)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")
