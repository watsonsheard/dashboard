"""One-time Garmin login → prints a token you paste into the GitHub secret GARMINTOKENS.

Run in YOUR OWN terminal (so you can type your password + 2-step code):

    C:\\Python314\\python.exe -m pip install garth garminconnect
    C:\\Python314\\python.exe scripts\\garmin_login.py

Your email/password/2-step code are entered locally and are NEVER stored or shared.
Only the resulting token (which auto-refreshes for ~a year) goes into GitHub.

If you see "429" / "rate limited": Garmin is throttling logins from your IP.
Wait ~30-60 minutes, then run this ONCE more (don't retry repeatedly - that
resets the timer).
"""
import sys
from getpass import getpass

try:
    import garth
except ImportError:
    sys.exit("First run:  C:\\Python314\\python.exe -m pip install garth garminconnect")

email = input("Garmin Connect email: ").strip()
password = getpass("Garmin Connect password (hidden as you type): ")

try:
    # garth.login prompts for the 2-step / MFA code automatically if needed
    garth.login(email, password)
except Exception as e:
    msg = str(e)
    print("\nLogin did not complete:", msg)
    if "429" in msg or "rate" in msg.lower():
        print("\n>>> That's Garmin rate-limiting your IP. Wait ~30-60 min, then run this ONCE more.")
    else:
        print("\n>>> Double-check your email/password. If 2-step is on, enter the code when asked.")
    sys.exit(1)

token = garth.client.dumps()
print("\n" + "=" * 64)
print("COPY THE ENTIRE TOKEN BELOW  ->  GitHub secret named  GARMINTOKENS")
print("=" * 64 + "\n")
print(token)
print("\n" + "=" * 64)
print("Done. Paste that into GitHub, then you can close this window.")
