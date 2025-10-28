import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('OPENAI_API_KEY')

print(f'Length: {len(key)}')
print(f'Has spaces: {" " in key}')
print(f'Has newlines: {chr(10) in key or chr(13) in key}')
print(f'First char code: {ord(key[0])}')
print(f'Last char code: {ord(key[-1])}')
print(f'Key repr: {repr(key[:30])}...{repr(key[-30:])}')

