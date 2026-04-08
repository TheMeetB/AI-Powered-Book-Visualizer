from dotenv import load_dotenv
import os
load_dotenv()

from App.config import database

try:
    res = database.command("ping")
    print("Ping result:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
