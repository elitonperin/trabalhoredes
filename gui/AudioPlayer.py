import wave

import pyaudio


class AudioPlayer:
    def __init__(self, file_name):
        self.file_name = file_name

    def start_audio(self):
        chunk = 1024
        wf = wave.open(self.file_name, 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(format=
                        p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(chunk)

        while data != b'':
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()

        p.terminate()