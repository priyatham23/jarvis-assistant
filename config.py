import os 
from dotenv import load_dotenv 
load_dotenv() 
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "") 
MODEL_NAME = "llama3.2" 
