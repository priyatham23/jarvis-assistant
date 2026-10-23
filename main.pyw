import os
import sys
import wave
import struct
import threading
import win32com.client
import speech_recognition as sr
import ollama
import keyboard
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
    """Asks user for verbal confirmation before executing any tool."""
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

def process_voice_command(recorder, messages):
    """Core voice loop processing triggered via hotkey or voice cycle."""
    user_input = listen_pvrecorder(recorder, timeout_secs=6)
    if not user_input:
        return

    user_lower = user_input.lower()
    messages.append({"role": "user", "content": user_input})

    # DYNAMIC TOOL ROUTING
    active_tools = []
    if "scroll" in user_lower:
        active_tools = [tools_map["scroll_page"]]
    elif "skip" in user_lower:
        active_tools = [tools_map["skip_youtube_ad"]]
    elif "minimize" in user_lower:
        active_tools = [tools_map["minimize_all_windows"]]
    elif "close" in user_lower:
        active_tools = [tools_map["close_active_window"]]
    elif any(kw in user_lower for kw in ["clipboard", "copy", "paste", "read clipboard"]):
        active_tools = [tools_map["read_clipboard"], tools_map["copy_to_clipboard"]]
    elif any(kw in user_lower for kw in ["screen", "look at my screen", "what is on my screen", "see screen"]):
        active_tools = [tools_map["analyze_screen"]]
    elif any(kw in user_lower for kw in ["play youtube", "play on youtube"]):
        active_tools = [tools_map["play_youtube"]]
    elif any(kw in user_lower for kw in ["open", "launch", "volume", "screenshot", "shutdown", "restart", "lock", "my notes"]):
        active_tools = tools_list

    response = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
        tools=active_tools if active_tools else None
    )

    if response.get("message", {}).get("tool_calls"):
        for tool_call in response["message"]["tool_calls"]:
            fn_name = tool_call["function"]["name"]
            args = tool_call["function"]["arguments"]

            if fn_name in tools_map:
                action_desc = f"execute {fn_name}"
                if fn_name == "scroll_page":
                    action_desc = f"scroll {args.get('direction', 'down')}"
                elif fn_name in ["minimize_all_windows", "minimize_window", "minimize"]:
                    action_desc = "minimize active window"
                elif fn_name == "analyze_screen":
                    action_desc = "analyze screen contents"
                elif fn_name == "read_clipboard":
                    action_desc = "read clipboard content"

                if confirm_permission(action_desc, recorder):
                    result = tools_map[fn_name](**args)
                    speak(result)
                    messages.append(response["message"])
                    messages.append({"role": "tool", "content": result, "name": fn_name})
    else:
        reply = response["message"]["content"]
        speak(reply)
        messages.append({"role": "assistant", "content": reply})

# System Tray Icon Setup
def create_tray_icon(recorder, messages):
    def on_quit(icon, item):
        icon.stop()
        os._exit(0)

    image = Image.new('RGB', (64, 64), color=(0, 120, 215))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(255, 255, 255))

    menu = pystray.Menu(
        pystray.MenuItem("JARVIS Active (Ctrl+Space to talk)", lambda: None, enabled=False),
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
                "You are JARVIS, a concise local voice assistant. "
                "Answer questions directly in one short sentence using your internal brain. "
                "Never invoke tools unless explicitly requested."
            )
        }
    ]

    # Register Global Hotkey (Ctrl + Space)
    def on_hotkey():
        speak("Listening, boss...")
        process_voice_command(recorder, messages)

    keyboard.add_hotkey('ctrl+space', on_hotkey)
    speak("JARVIS activated. Press Ctrl+Space anytime to talk, boss.")

    # Run System Tray in background thread
    tray_thread = threading.Thread(target=create_tray_icon, args=(recorder, messages), daemon=True)
    tray_thread.start()

    # Main loop waiting for hotkey activations
    keyboard.wait()

if __name__ == "__main__":
    run_jarvis()