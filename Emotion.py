from google.cloud import speech
import io
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pydub import AudioSegment
from pydub.playback import play
import os
import speech_recognition as sr

# Function to check vulgarity
def check_vulgarity(text, vulgar_words):
    words = text.split()
    vulgar_count = sum(1 for word in words if word.lower() in vulgar_words)
    vulgar_percentage = (vulgar_count / len(words)) * 100 if words else 0
    return vulgar_percentage

# List of vulgar words (expand as needed)
vulgar_words = ['bastard', 'fool', 'stupid']  # Replace with actual vulgar words

# Threshold for vulgarity
vulgarity_threshold = 20.0  # Adjust the threshold as per your requirement

def transcribe_audio_google(audio_file):
    client = speech.SpeechClient()

    # Load audio data into memory
    with io.open(audio_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    # Get the transcription of the first result
    for result in response.results:
        return result.alternatives[0].transcript

def record_audio():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print('Clearing background noise...')
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print('Waiting for your message...')
        recorded_audio = recognizer.listen(source)
        print('Done recording.')

        # Save the recorded audio as a WAV file
        audio_file_path = "temp_audio.wav"
        with open(audio_file_path, "wb") as f:
            f.write(recorded_audio.get_wav_data())
        return audio_file_path

try:
    # Prompt user to start recording
    start_recording = input("Do you want to start recording? (yes/no): ").lower()

    if start_recording == 'yes':
        # Record the audio
        audio_file_path = record_audio()

        # Transcribe the recorded audio using Google Cloud
        print("Transcribing audio using Google Cloud Speech-to-Text...")
        text = transcribe_audio_google(audio_file_path)
        print('Your message: {}'.format(text))

        # Check for vulgarity
        vulgar_percentage = check_vulgarity(text, vulgar_words)
        print(f'Vulgarity percentage: {vulgar_percentage:.2f}%')

        # Sentiment analysis
        analyser = SentimentIntensityAnalyzer()
        sentiment_scores = analyser.polarity_scores(text)
        print(f'Sentiment analysis: {sentiment_scores}')

        # Check if vulgarity exceeds the threshold
        if vulgar_percentage > vulgarity_threshold:
            print(f'Vulgarity exceeded {vulgarity_threshold}%! Saving audio...')

            # Save the audio as MP3
            mp3_file_path = "recorded_audio.mp3"
            audio = AudioSegment.from_wav(audio_file_path)
            audio.export(mp3_file_path, format="mp3")
            print(f"Audio saved as {mp3_file_path}")
    else:
        print("Recording canceled.")

except Exception as ex:
    print(f"Error: {ex}")
