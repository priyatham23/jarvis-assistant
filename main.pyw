import os
import pyttsx3
import speech_recognition as sr
import ollama
import pvporcupine
from pvrecorder import PvRecorder

from config import PICOVOICE_ACCESS_KEY, MODEL_NAME
from tools import tools_list, tools_map

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text: str):
    print(f"\nJARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

def listen() -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[ Listening... ]")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio)
            print(f"You: {query}")
            return query
        except Exception:
            return ""

def run_jarvis():
    # Initialize Picovoice Porcupine Wake-Word Detector
    porcupine = pvporcupine.create(
        access_key=PICOVOICE_ACCESS_KEY,
        keywords=["jarvis"]
    )
    recorder = PvRecorder(frame_length=porcupine.frame_length)
    recorder.start()

    messages = [
        {
            "role": "system",
            "content": (
                "You are JARVIS, a helpful local AI assistant. "
                "Keep verbal responses concise, direct, and clear. "
                "Use available tools to perform laptop actions or search personal notes."
            )
        }
    ]

    speak("JARVIS systems active in the background.")

    try:
        while True:
            pcm = recorder.read()
            keyword_index = porcupine.process(pcm)

            # Triggered when "Jarvis" wake-word is detected
            if keyword_index >= 0:
                speak("Yes, boss?")
                recorder.stop()

                user_input = listen()
                if user_input:
                    if any(w in user_input.lower() for w in ["exit", "shutdown", "stop", "sleep"]):
                        speak("Going offline, boss. Have a good day!")
                        break

                    messages.append({"role": "user", "content": user_input})

                    # Send request to local Ollama with tools
                    response = ollama.chat(
                        model=MODEL_NAME,
                        messages=messages,
                        tools=tools_list
                    )

                    # Check for tool execution
                    if response.get("message", {}).get("tool_calls"):
                        for tool_call in response["message"]["tool_calls"]:
                            fn_name = tool_call["function"]["name"]
                            args = tool_call["function"]["arguments"]

                            if fn_name in tools_map:
                                result = tools_map[fn_name](**args)
                                speak(result)
                                messages.append(response["message"])
                                messages.append({
                                    "role": "tool",
                                    "content": result,
                                    "name": fn_name
                                })
                    else:
                        reply = response["message"]["content"]
                        speak(reply)
                        messages.append({"role": "assistant", "content": reply})

                recorder.start()

    finally:
        recorder.stop()
        recorder.delete()
        porcupine.delete()

if __name__ == "__main__":
    run_jarvis()