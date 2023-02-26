import os
from dotenv import load_dotenv

load_dotenv()

print('Database URL:', os.environ['DATABASE_URL'])
