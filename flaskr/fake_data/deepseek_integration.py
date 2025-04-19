import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://openrouter.ai/api/v1")

def generate_cities_for_countries(countries: list[str], min_count: int = 2, max_count: int = 8, max_retries: int = 3) -> dict[str, list[str]]:
    prompt = (
        f"I have the following countries: {countries}. "
        f"For each country, generate between {min_count} and {max_count} "
        "major city names. Output EXACTLY a JSON object where each key "
        "is the country name and its value is an array of city names."
    )
    for attempt in range(1, max_retries + 1):
        resp = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "system", "content": "You are a JSON‑output assistant."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.7,
            stream=False
        )
        choice = resp.choices[0] if resp.choices else None
        if choice and getattr(choice, "error", None):
            err = choice.error
            retryable = err.get("metadata", {}).get("raw", {}).get("retryable", False)
            if attempt < max_retries and retryable:
                continue
            raise RuntimeError(f"DeepSeek error on attempt {attempt}: {err}")
        raw = None
        if choice and getattr(choice, "message", None):
            raw = choice.message.content
        elif choice and getattr(choice, "text", None):
            raw = choice.text

        if not raw:
            raise RuntimeError(f"No content returned by DeepSeek on attempt {attempt}:\n{resp}")

        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].endswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        if not text:
            raise RuntimeError(f"DeepSeek returned an empty string for countries on attempt {attempt}.")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON (error: {e})\nReturned text:\n{text}")

        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object, got {type(data)}:\n{data}")
        missing = set(countries) - set(data.keys())
        if missing:
            raise ValueError(f"Missing keys for countries: {missing}\nGot:\n{data.keys()}")
        return data
    raise RuntimeError("Exhausted retries in generate_cities_for_countries")

def generate_addresses_for_cities(country: str, cities: list[str], min_address: int = 5, max_address: int = 15) -> dict[str, list[dict]]:
    system_msg = (
        "You are a JSON-output assistant."
        "Given a country and a list of cities, produce exactly a JSON object "
        "where each key is a city name and its value is an array of unique street "
        "address objects (with address1, address2, state, zipcode)."
    )
    user_payload = {
        "country": country,
        "cities": cities,
        "min_addresses_per_city": min_address,
        "max_addresses_per_city": max_address
    }

    resp = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": json.dumps(user_payload)}
        ],
        temperature=0.7,
        stream=False
    )
    choice = resp.choices[0] if resp.choices else None
    raw = None
    if choice and getattr(choice, "message", None):
        raw = choice.message.content
    elif choice and getattr(choice, "text", None):
        raw = choice.text

    if raw is None:
        raise RuntimeError(
            f"No content found in response for {country}. Full response:\n{resp}"
        )
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].endswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    if not text:
        raise ValueError("Empty response from DeepSeek.")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON for {country} (error: {e}).\n"
            f"String was:\n{text}"
        )
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object, got {type(data)}:\n{data}")
    return data


def generate_doctor_profiles(count: int = 20) -> list[dict]:
    system_msg = (
        "You are a JSON-output assistant."
        f"output only contains an array of {count} JSON objects"
        "no yapping, no explanations, no extra text, no markdown fences. "
        "using *double quotes* for all keys and strings, and no markdown fences. "
        "where each key is first_name, last_name, specialization(real medical specialty) and bio (~80-word paragraph)"
    )
    resp = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {"role":"system", "content": system_msg},
            {"role":"user",   "content": json.dumps({"count": count})}
        ],
        temperature=0.7,
        stream=False
    )
    choice = resp.choices[0] if resp.choices else None
    raw = None
    if choice and getattr(choice, "message", None):
        raw = choice.message.content
    elif choice and getattr(choice, "text", None):
        raw = choice.text

    if not raw:
        raise RuntimeError(f"No content in response:\n{resp}")

    text = raw.strip()

    if text.startswith("```"):
        lines = text.splitlines()
    
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].endswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    if not text:
        raise ValueError("DeepSeek returned an empty response.")
    try:
        profiles = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON (error: {e})\n"
            f"String was:\n{text}"
        )
    if not (isinstance(profiles, list) and len(profiles) == count):
        raise ValueError(
            f"Expected a list of length {count}, got {type(profiles)} with length "
            f"{len(profiles) if isinstance(profiles, list) else 'N/A'}:\n{profiles}"
        )
    return profiles