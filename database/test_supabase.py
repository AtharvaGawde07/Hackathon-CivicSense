import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SECRET_KEY")

if not url or not key:
    raise RuntimeError("Missing Supabase environment variables.")

supabase = create_client(url, key)

response = (
    supabase
    .table("reports")
    .select("id")
    .limit(1)
    .execute()
)

print("Supabase connection successful.")
print(response.data)