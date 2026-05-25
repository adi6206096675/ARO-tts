from gtts import gTTS
import os

def generate_aro_audio(text, filename="aro_output.mp3"):
    print(f"Aro is processing: '{text}'...")
    
    # Generate the speech
    tts = gTTS(text=text, lang='en', slow=False)
    
    # Save the audio file
    tts.save(filename)
    print(f"Success! Audio saved as {filename}")

if __name__ == "__main__":
    # This is the text Aro will read
    sample_text = "Hello! Welcome to Aro, your new text to speech service. I am alive and ready to read."
    
    generate_aro_audio(sample_text)