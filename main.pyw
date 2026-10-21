import os
import pyttsx3
import speech_recognition as sr
import ollama
import pvporcupine
from pvrecorder import PvRecorder

from config import PICOVOICE_ACCESS_KEY, MODEL_NAME
from tools import tools_list, tools_map

engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text: str):
    print(f"\nJARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

def listen(timeout_secs=5) -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[ Listening... ]")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=timeout_secs)
            query = recognizer.recognize_google(audio)
            print(f"You: {query}")
            return query
        except Exception:
            return ""

def confirm_permission(action_description: str) -> bool:
    """Asks the user for explicit permission before executing any system tool."""
    speak(f"Boss, you requested to {action_description}. Do I have your permission to proceed?")
    user_response = listen(timeout_secs=4).lower()
    
    # Strictly require explicit positive confirmation
    if any(word in user_response for word in ["yes", "yeah", "sure", "proceed", "do it", "confirm", "ok"]):
        return True
    
    speak("Action canceled, boss.")
    return False

def run_jarvis():
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

    speak("JARVIS systems active in background with permission controls enabled.")

    try:
        while True:
            pcm = recorder.read()
            if porcupine.process(pcm) >= 0:
                speak("Yes, boss?")
                recorder.stop()

                user_input = listen()
                if user_input:
                    if any(w in user_input.lower() for w in ["exit", "shutdown", "stop", "sleep"]):
                        speak("Going offline, boss.")
                        break

                    messages.append({"role": "user", "content": user_input})

                    response = ollama.chat(
                        model=MODEL_NAME,
                        messages=messages,
                        tools=tools_list
                    )

                    # Check if Ollama wants to call a tool
                    if response.get("message", {}).get("tool_calls"):
                        for tool_call in response["message"]["tool_calls"]:
                            fn_name = tool_call["function"]["name"]
                            args = tool_call["function"]["arguments"]

                            if fn_name in tools_map:
                                action_desc = f"execute {fn_name}"
                                if fn_name == "open_website":
                                    action_desc = f"open {args.get('url', 'the website')}"
                                elif fn_name == "play_youtube":
                                    action_desc = f"play '{args.get('topic', '')}' on YouTube"
                                elif fn_name == "set_volume":
                                    action_desc = f"set system volume to {args.get('level', '')}%"

                                # PERMISSION GUARD
                                if confirm_permission(action_desc):
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