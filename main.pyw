import os
import wave
import struct
import win32com.client
import speech_recognition as sr
import ollama
from pvrecorder import PvRecorder

from config import MODEL_NAME
from tools import tools_list, tools_map

# Initialize Direct Windows SAPI Voice Driver
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text: str):
    print(f"\nJARVIS: {text}")
    try:
        speaker.Speak(text)
    except Exception as e:
        print(f"[TTS Error]: {e}")

def listen_pvrecorder(recorder, timeout_secs=5) -> str:
    """Listens to microphone using PvRecorder and converts speech to text."""
    recognizer = sr.Recognizer()
    frames = []
    print("\n[ Listening... ]")
    
    recorder.start()
    try:
        max_frames = int((recorder.sample_rate / recorder.frame_length) * timeout_secs)
        for _ in range(max_frames):
            frame = recorder.read()
            frames.extend(frame)
    finally:
        recorder.stop()

    byte_data = struct.pack("<" + "h" * len(frames), *frames)
    audio_data = sr.AudioData(byte_data, recorder.sample_rate, 2)

    try:
        query = recognizer.recognize_google(audio_data)
        print(f"You: {query}")
        return query
    except Exception:
        return ""

def confirm_permission(action_description: str, recorder) -> bool:
    """Asks user for verbal confirmation before executing any tool.
    Strictly denies execution unless an explicit positive confirmation word is present.
    """
    speak(f"Boss, you requested to {action_description}. Do I have your permission to proceed?")
    
    user_response = listen_pvrecorder(recorder, timeout_secs=5).strip().lower()
    
    allowed_words = [
        "yes", "yeah", "sure", "proceed", "do it", "confirm", "ok", "okay",
        "permission", "granted", "go ahead", "allow", "approved"
    ]
    
    if user_response and any(word in user_response for word in allowed_words):
        speak("Permission granted. Executing now, boss.")
        return True
    
    speak("Permission denied. Action canceled, boss.")
    return False

def run_jarvis():
    recorder = PvRecorder(frame_length=512)
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

    speak("JARVIS systems active and ready, boss.")

    try:
        while True:
            user_input = listen_pvrecorder(recorder, timeout_secs=6)
            
            if user_input:
                if any(w in user_input.lower() for w in ["exit", "shutdown assistant", "stop", "sleep", "go offline"]):
                    speak("Going offline, boss.")
                    break

                messages.append({"role": "user", "content": user_input})

                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=tools_list
                )

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
                            elif fn_name == "take_screenshot":
                                action_desc = "take a screenshot"
                            elif fn_name == "open_app":
                                action_desc = f"open the application {args.get('app_name', '')}"
                            elif fn_name == "close_active_window":
                                action_desc = "close the active window"
                            elif fn_name == "minimize_all_windows":
                                action_desc = "minimize all open windows"
                            elif fn_name == "system_power_control":
                                action_desc = f"perform system {args.get('action', 'power action')}"

                            # STRICT PERMISSION GUARD
                            if confirm_permission(action_desc, recorder):
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

    finally:
        recorder.delete()

if __name__ == "__main__":
    run_jarvis()