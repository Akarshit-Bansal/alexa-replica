import pvporcupine
import pyaudio
import struct

class HotwordDetector:
    def __init__(self, access_key, keyword='alexa'):
        self.porcupine = pvporcupine.create(access_key=access_key, keywords=[keyword])
        self.audio_stream = None

    def start_listening(self):
        self.audio_stream = pyaudio.PyAudio().open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def detect(self):
        pcm = self.audio_stream.read(self.porcupine.frame_length)
        pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
        keyword_index = self.porcupine.process(pcm)
        return keyword_index >= 0

    def stop(self):
        if self.audio_stream:
            self.audio_stream.close()
        self.porcupine.delete()
