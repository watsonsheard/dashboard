"""Fetch Garmin daily stats and write them ENCRYPTED to data/garmin.enc.json.

Runs in GitHub Actions on a schedule. Reads two secrets from the environment:
  GARMINTOKENS  - the garth token string (from scripts/garmin_login.py)
  DASH_PASSCODE - the dashboard passcode (used to encrypt, so only you can read it)

Encryption matches the browser (WebCrypto): PBKDF2-SHA256 (200k iters, 16-byte
salt) -> AES-256-GCM (12-byte IV, tag appended to ciphertext).

Test the encryption locally without Garmin:
  DASH_PASSCODE=otter-cedar-60 C:\\Python314\\python.exe scripts\\fetch_garmin.py --sample
"""
import os, sys, json, base64, hashlib, datetime

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PBKDF2_ITERS = 200_000
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "garmin.enc.json")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def encrypt(payload: dict, passcode: str) -> dict:
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = hashlib.pbkdf2_hmac("sha256", passcode.encode(), salt, PBKDF2_ITERS, dklen=32)
    ct = AESGCM(key).encrypt(iv, json.dumps(payload).encode(), None)
    b64 = lambda b: base64.b64encode(b).decode()
    return {"v": 1, "salt": b64(salt), "iv": b64(iv), "ct": b64(ct), "updated": payload.get("updated")}


def sample_payload() -> dict:
    return {
        "updated": now_iso(),
        "steps": {"value": 8432, "goal": 10000},
        "calories": {"active": 612, "resting": 1500},
        "distance_mi": 4.2,
        "sleep_h": 7.2,
        "resting_hr": {"value": 54, "delta": -2},
        "weight_lb": {"value": 168.4, "delta": -0.6},
    }


def garmin_payload() -> dict:
    """Best-effort pull from Garmin via the garth token. Each metric is guarded so a
    single failing endpoint never sinks the whole run."""
    import garth
    garth.client.loads(os.environ["GARMINTOKENS"])
    display = garth.client.profile["displayName"]
    today = datetime.date.today()
    d = today.isoformat()

    def api(path, **params):
        return garth.client.connectapi(path, params=params or None)

    out = {"updated": now_iso()}

    try:
        s = api(f"/usersummary-service/usersummary/daily/{display}", calendarDate=d) or {}
        if s.get("totalSteps") is not None:
            out["steps"] = {"value": int(s["totalSteps"]),
                            "goal": int(s.get("dailyStepGoal") or 10000)}
        if s.get("activeKilocalories") is not None or s.get("bmrKilocalories") is not None:
            out["calories"] = {"active": int(s.get("activeKilocalories") or 0),
                               "resting": int(s.get("bmrKilocalories") or 0)}
        if s.get("totalDistanceMeters"):
            out["distance_mi"] = round(s["totalDistanceMeters"] / 1609.344, 1)
        if s.get("restingHeartRate"):
            out["resting_hr"] = {"value": int(s["restingHeartRate"])}
    except Exception as e:
        print("[garmin] daily summary failed:", e)

    try:
        sl = api(f"/wellness-service/wellness/dailySleepData/{display}", date=d) or {}
        secs = (sl.get("dailySleepDTO") or {}).get("sleepTimeSeconds")
        if secs:
            out["sleep_h"] = round(secs / 3600, 1)
    except Exception as e:
        print("[garmin] sleep failed:", e)

    try:
        w = api(f"/weight-service/weight/dayview/{d}") or {}
        rows = w.get("dateWeightList") or []
        if rows:
            grams = rows[-1].get("weight")
            if grams:
                out["weight_lb"] = {"value": round(grams / 453.592, 1)}
    except Exception as e:
        print("[garmin] weight failed:", e)

    return out


def main():
    passcode = os.environ.get("DASH_PASSCODE")
    if not passcode:
        sys.exit("DASH_PASSCODE env var is required.")

    if "--sample" in sys.argv:
        payload = sample_payload()
        print("Using SAMPLE data.")
    else:
        payload = garmin_payload()
        print("Fetched from Garmin:", json.dumps({k: v for k, v in payload.items() if k != 'updated'}))

    blob = encrypt(payload, passcode)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(blob, f)
    print("Wrote", os.path.relpath(OUT_PATH))


if __name__ == "__main__":
    main()
