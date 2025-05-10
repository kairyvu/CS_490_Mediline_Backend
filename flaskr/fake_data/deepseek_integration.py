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
            model="deepseek/deepseek-prover-v2:free",
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
        if not text:
            if attempt < max_retries:
                continue
            raise ValueError("DeepSeek returned an empty response.")
        start = text.find('{')
        end   = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
        else:
            if attempt < max_retries:
                continue
            raise ValueError(f"Could not locate JSON array in response on attempt {attempt}:\n{text}")
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

def generate_addresses_for_cities(country: str, cities: list[str], min_address: int = 5, max_address: int = 15, max_retries: int = 3) -> dict[str, list[dict]]:
    system_msg = (
        "You are a JSON-output assistant."
        "Given a country and a list of cities, produce exactly a JSON object "
        "where each key is a city name and its value is an array of unique street "
        "each address object must be separated by a comma. "
        "address objects (with address1, address2, state, zipcode)."
    )
    user_payload = {
        "country": country,
        "cities": cities,
        "min_addresses_per_city": min_address,
        "max_addresses_per_city": max_address
    }
    for attempt in range(1, max_retries + 1):
        resp = client.chat.completions.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": json.dumps(user_payload)}
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

        if raw is None:
            raise RuntimeError(
                f"No content found in response for {country}. Full response:\n{resp}"
            )
        text = raw.strip()
        if not text:
            if attempt < max_retries:
                continue
            raise ValueError("DeepSeek returned an empty response.")
        start = text.find('{')
        end   = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
        else:
            if attempt < max_retries:
                continue
            raise ValueError(f"Could not locate JSON array in response on attempt {attempt}:\n{text}")
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


def generate_doctor_profiles(count: int = 20, max_retries: int = 3) -> list[dict]:
    system_msg = (
        "You are a JSON-output assistant."
        f"output only contains an array of {count} JSON objects"
        "no yapping, no explanations, no extra text, no markdown fences. "
        "using *double quotes* for all keys and strings, and no markdown fences. "
        "where each key is first_name, last_name, gender, specialization(real medical specialty) and bio (~80-word paragraph)"
    )
    for attempt in range(1, max_retries + 1):
        resp = client.chat.completions.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=[
                {"role":"system", "content": system_msg},
                {"role":"user",   "content": json.dumps({"count": count})}
            ],
            temperature=0.7,
            stream=False,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "doctor_profile",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "first_name": {
                                "type": "string",
                                "description": "A doctor's First Name"
                            },
                            "last_name": {
                                "type": "string",
                                "description": "A doctor's Last Name"
                            },
                            "gender": {
                                "type": "string",
                                "description": "A doctor's gender"
                            },
                            "specialization": {
                                "type": "string",
                                "description": "A medical specialty"
                            },
                            "bio": {
                                "type": "string",
                                "description": "A doctor's bio for an online platform where they advertise their service given their specialization"
                            }
                        }
                    }
                }
            }
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
            raise RuntimeError(f"No content in response:\n{resp}")

        text = raw.strip()
        if not text:
            if attempt < max_retries:
                continue
            raise ValueError("DeepSeek returned an empty response.")
        start = text.find('[')
        end   = text.rfind(']')
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
        else:
            if attempt < max_retries:
                continue
            raise ValueError(f"Could not locate JSON array in response on attempt {attempt}:\n{text}")
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
    
def generate_exercises(count: int = 20, max_retries: int = 3) -> list[dict]:
    system_msg = (
        "You are a JSON-output assistant."
        f"output only contains an array of {count} JSON objects"
        "no yapping, no explanations, no extra text, no markdown fences. "
        "using *double quotes* for all keys and strings, and no markdown fences. "
        "where each key is type_of_exercise, description"
    )
    for attempt in range(1, max_retries + 1):
        resp = client.chat.completions.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=[
                {"role":"system", "content": system_msg},
                {"role":"user",   "content": json.dumps({"count": count})}
            ],
            temperature=0.7,
            stream=False,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "exercise",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "type_of_exercise": {
                                "type": "string",
                                "description": "A name of an exercise"
                            },
                            "description": {
                                "type": "string",
                                "description": "A description of the exercise"
                            },
                        }
                    }
                }
            }
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
            raise RuntimeError(f"No content in response:\n{resp}")
        text = raw.strip()
        if not text:
            if attempt < max_retries:
                continue
            raise ValueError("DeepSeek returned an empty response.")
        start = text.find('[')
        end   = text.rfind(']')
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
        else:
            if attempt < max_retries:
                continue
            raise ValueError(f"Could not locate JSON array in response on attempt {attempt}:\n{text}")
        try:
            exercises = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON (error: {e})\n"
                f"String was:\n{text}"
            )
        return exercises
    raise RuntimeError("Exhausted retries in generate_exercises")

def generate_medications(count: int = 50, max_retries: int = 3) -> list[dict]:
    system_msg = (
        "You are a JSON-output assistant."
        f"output only contains an array of {count} JSON objects"
        "no yapping, no explanations, no extra text, no markdown fences. "
        "using *double quotes* for all keys and strings, and no markdown fences. "
        "where each key is medication_name, medication_description"
    )
    for attempt in range(1, max_retries + 1):
        resp = client.chat.completions.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=[
                {"role":"system", "content": system_msg},
                {"role":"user",   "content": json.dumps({"count": count})}
            ],
            temperature=0.7,
            stream=False,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "medication",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "medication_name": {
                                "type": "string",
                                "description": "The name of the medicine"
                            },
                            "medication_description": {
                                "type": "string",
                                "description": "A description of the medication"
                            },
                        }
                    }
                }
            }
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
            raise RuntimeError(f"No content in response:\n{resp}")
        text = raw.strip()
        if not text:
            if attempt < max_retries:
                continue
            raise ValueError("DeepSeek returned an empty response.")
        start = text.find('[')
        end   = text.rfind(']')
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
        else:
            if attempt < max_retries:
                continue
            raise ValueError(f"Could not locate JSON array in response on attempt {attempt}:\n{text}")
        try:
            medications = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON (error: {e})\n"
                f"String was:\n{text}"
            )
        return medications
    raise RuntimeError("Exhausted retries in generate_medications")

def generate_social_media_posts(count: int = 30, max_retries: int = 3) -> list[dict]:
    system_msg = (
        "You are a JSON-output assistant."
        f"output only contains an array of {count} JSON objects"
        "no yapping, no explanations, no extra text, no markdown fences. "
        "using *double quotes* for all keys and strings, and no markdown fences. "
        "where each key is title, content and both should be medical related"
    )
    for attempt in range(1, max_retries + 1):
        resp = client.chat.completions.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=[
                {"role":"system", "content": system_msg},
                {"role":"user",   "content": json.dumps({"count": count})}
            ],
            temperature=0.7,
            stream=False,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "medical_social_media_post",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the post relating to medical field"
                            },
                            "content": {
                                "type": "string",
                                "description": "The content of the post relating to medical field"
                            },
                        }
                    }
                }
            }
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
            if attempt < max_retries:
                continue
            raise RuntimeError(f"No content in response:\n{resp}")
        text = raw.strip()
        if not text:
            if attempt < max_retries:
                continue
            raise ValueError("DeepSeek returned an empty response.")
        start = text.find('[')
        end   = text.rfind(']')
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
        else:
            if attempt < max_retries:
                continue
            raise ValueError(f"Could not locate JSON array in response on attempt {attempt}:\n{text}")
        try:
            posts = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON (error: {e})\n"
                f"String was:\n{text}"
            )
        return posts
    raise RuntimeError("Exhausted retries in generate_social_media_posts")

if __name__ == "__main__":
    print(generate_doctor_profiles())