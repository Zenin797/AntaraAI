from RealtimeTTS import TextToAudioStream, EdgeEngine

engine = EdgeEngine()

stream = TextToAudioStream(engine)
stream.feed("Aap aaj yahan kese aye?")
stream.play_async()