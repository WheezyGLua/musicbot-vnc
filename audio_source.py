
import discord
import soundcard as sc
import numpy as np

class SystemAudioSource(discord.AudioSource):
    def __init__(self):
        self.sample_rate = 48000
        self.channels = 2
        
        # Get the default speaker
        self.speaker = sc.default_speaker()
        
        # Create a recorder using the loopback feature of the speaker
        # Blocksize is calculated for 20ms of audio (Discord's preferred frame size)
        # 48000 Hz * 0.02 s = 960 samples
        self.blocksize = 960
        self.recorder = self.speaker.recorder(samplerate=self.sample_rate, channels=self.channels, blocksize=self.blocksize)
        
        # We need to open the recorder in a context manager conceptually, but AudioSource is driven by read() calls.
        # So we'll enter the context manually.
        self.recorder_context = self.recorder.__enter__()
        
    def read(self):
        # Record a chunk of audio
        # soundcard returns float32 [-1.0, 1.0], we need 16-bit PCM bytes
        data = self.recorder_context.record(numframes=self.blocksize)
        
        # Convert float32 to int16
        # Clip to ensure no overflow
        pcm_data = (np.clip(data, -1.0, 1.0) * 32767).astype(np.int16)
        
        # Convert to bytes (tobytes() works for numpy arrays)
        return pcm_data.tobytes()

    def cleanup(self):
        # Exit the recorder context when done
        if self.recorder_context:
            self.recorder.__exit__(None, None, None)
            self.recorder_context = None

    def __del__(self):
        self.cleanup()
