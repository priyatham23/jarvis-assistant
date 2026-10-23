import os
import sys
import wave
import struct
import threading
import win32com.client
import speech_recognition as sr
import ollama
import pystray
from PIL import Image, ImageDraw
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
    """Listens continuously to the microphone and converts speech to text."""
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

def process_voice_command(user_input: str, messages: list):
    """Executes voice commands instantly without asking for permission prompts."""
    user_lower = user_input.lower()
    messages.append({"role": "user", "content": user_input})

    # FAST DYNAMIC TOOL ROUTER
    active_tools = None
    if "scroll" in user_lower:
        active_tools = [tools_map["scroll_page"]]
    elif "skip" in user_lower:
        active_tools = [tools_map["skip_youtube_ad"]]
    elif "minimize" in user_lower:
        active_tools = [tools_map["minimize_all_windows"]]
    elif "close" in user_lower:
        active_tools = [tools_map["close_active_window"]]
    elif any(kw in user_lower for kw in ["full screen", "fullscreen"]):
        active_tools = [tools_map["toggle_full_screen"]]
    elif any(kw in user_lower for kw in ["pause", "play video", "resume"]):
        active_tools = [tools_map["toggle_play_pause"]]
    elif any(kw in user_lower for kw in ["increase volume", "volume up", "louder"]):
        active_tools = [tools_map["volume_up"]]
    elif any(kw in user_lower for kw in ["decrease volume", "volume down", "quieter"]):
        active_tools = [tools_map["volume_down"]]
    elif any(kw in user_lower for kw in ["clipboard", "copy", "paste"]):
        active_tools = [tools_map["read_clipboard"], tools_map["copy_to_clipboard"]]
    elif any(kw in user_lower for kw in ["screen", "look at my screen", "see screen"]):
        active_tools = [tools_map["analyze_screen"]]
    elif "youtube" in user_lower and "play" in user_lower:
        active_tools = [tools_map["play_youtube"]]
    elif any(kw in user_lower for kw in ["open", "launch", "volume", "screenshot", "shutdown", "restart"]):
        active_tools = tools_list

    response = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
        tools=active_tools
    )

    if response.get("message", {}).get("tool_calls"):
        for tool_call in response["message"]["tool_calls"]:
            fn_name = tool_call["function"]["name"]
            args = tool_call["function"]["arguments"]

            if fn_name in tools_map:
                result = tools_map[fn_name](**args)
                speak(result)
                messages.append(response["message"])
                messages.append({"role": "tool", "content": result, "name": fn_name})
    else:
        reply = response["message"]["content"]
        speak(reply)
        messages.append({"role": "assistant", "content": reply})

def create_tray_icon():
    """System tray icon running in the background."""
    def on_quit(icon, item):
        icon.stop()
        os._exit(0)

    image = Image.new('RGB', (64, 64), color=(0, 120, 215))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(255, 255, 255))

    menu = pystray.Menu(
        pystray.MenuItem("JARVIS Active (Listening mode)", lambda: None, enabled=False),
        pystray.MenuItem("Exit JARVIS", on_quit)
    )
    
    icon = pystray.Icon("JARVIS", image, "JARVIS Assistant", menu)
    icon.run()

def run_jarvis():
    recorder = PvRecorder(frame_length=512)
    messages = [
        {
            "role": "system",
            "content": (
                "You are JARVIS, a helpful local voice assistant. "
                "Answer questions briefly in one short sentence. "
                "Execute system actions directly when commanded."
            )
        }
    ]

    speak("Welcome back, Boss. Your digital assistant is online, fully initialized, and ready to assist. I'm listening.")

    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

    try:
        while True:
            user_input = listen_pvrecorder(recorder, timeout_secs=5)
            if user_input:
                user_lower = user_input.lower()
                if any(w in user_lower for w in ["exit", "shutdown assistant", "stop", "sleep", "go offline"]):
                    speak("Going offline, boss.")
                    break
                process_voice_command(user_input, messages)
    finally:
        recorder.delete()

if __name__ == "__main__":
    run_jarvis()