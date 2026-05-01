import requests
import json
import re
import time
import urllib.parse
from typing import Type, TypeVar
from pydantic import BaseModel

from tools.common.messenger import Messenger

T = TypeVar("T", bound=BaseModel)

class PollinationsTextGenerator:
    """
    Free Text Generator using Pollinations.ai (No API key required).
    """
    post_url: str = "https://text.pollinations.ai/"
    get_url: str = "https://text.pollinations.ai/"

    def _unwrap_response(self, raw: str) -> str:
        """
        Handles ALL Pollinations response formats:
        1. Raw JSON: {"scenes": [...]}
        2. Wrapped: {"role":"assistant","content":"{...}","tool_calls":[]}
        3. Wrapped with dict content: {"role":"assistant","content":{...}}
        4. Raw text with markdown
        """
        raw = raw.strip()
        Messenger.info(f"[DEBUG] Raw response (first 200 chars): {raw[:200]}")
        
        # Attempt 1: Try json.loads to see if it's valid JSON
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                # Check if it's a wrapper response
                if "role" in parsed and "content" in parsed:
                    content = parsed["content"]
                    Messenger.info(f"[DEBUG] Unwrapped 'content' field, type: {type(content).__name__}")
                    if isinstance(content, dict):
                        # content is already a dict, convert back to JSON string
                        return json.dumps(content)
                    elif isinstance(content, str):
                        return content
                    else:
                        return str(content)
                elif "scenes" in parsed:
                    # Already a valid script JSON
                    return raw
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
        
        # Attempt 2: Try to find a wrapper with regex (for cases where json.loads fails)
        wrapper_match = re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.)*)"\s*[,}]', raw, re.DOTALL)
        if wrapper_match:
            content = wrapper_match.group(1)
            # Unescape JSON string
            content = content.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
            Messenger.info(f"[DEBUG] Extracted content via regex wrapper match")
            return content
        
        # Attempt 3: Check if content is a nested JSON object (not string)
        wrapper_match2 = re.search(r'"content"\s*:\s*(\{.*\})\s*[,}]', raw, re.DOTALL)
        if wrapper_match2:
            Messenger.info(f"[DEBUG] Extracted content as nested JSON object")
            return wrapper_match2.group(1)
        
        # Attempt 4: Return as-is
        return raw

    def _extract_scenes_json(self, content: str) -> str:
        """Extract and repair JSON containing scenes."""
        content = content.strip()
        
        # Clean markdown
        if "```" in content:
            content = re.sub(r'```(?:json)?\s*(.*?)\s*```', r'\1', content, flags=re.DOTALL)
        
        # Find JSON object
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in response")
        
        content = match.group(0)
        
        # Reject if it's still a wrapper
        if '"role"' in content and '"assistant"' in content and '"tool_calls"' in content:
            raise ValueError("Response is still a wrapper object, not a script")
        
        # Repair truncated JSON
        content = content.strip().rstrip(',')
        content = re.sub(r',\s*\]', ']', content)
        content = re.sub(r',\s*\}', '}', content)
        
        if not content.strip().endswith(']}'):
            last_brace = content.rfind('}')
            if last_brace != -1:
                content = content[:last_brace + 1]
            if '"scenes"' in content:
                while content.count('[') > content.count(']'):
                    content += ']'
                while content.count('{') > content.count('}'):
                    content += '}'
        
        while content.count('[') > content.count(']'):
            content += ']'
        while content.count('{') > content.count('}'):
            content += '}'
        
        return content

    def generate_text(self, prompt: str, schema: Type[T]) -> T:
        """Generates text with POST (primary) and GET (fallback)."""
        models = ["openai-fast", "openai", "gpt-oss"]
        last_error = None

        json_hint = (
            'Return ONLY a valid JSON object. No markdown, no explanation. '
            'Format: { "scenes": [ { "scene_number": 1, "narration": "...", '
            '"image_prompt": { "subjects": [{"description":"...", "action":"..."}], '
            '"environment": "...", "lighting": "...", "composition": "...", "style": "..." } } ] }'
        )
        system_prompt = f"You are a scriptwriter. MANDATORY: {json_hint}"

        for model in models:
            for attempt in range(3):
                try:
                    Messenger.info(f"Waiting 10s...")
                    time.sleep(10)
                    Messenger.info(f"--- Model: {model} | Try: {attempt+1} ---")
                    
                    raw_text = None
                    
                    # Try POST first
                    try:
                        payload = {
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            "model": model,
                            "jsonMode": True
                        }
                        resp = requests.post(self.post_url, json=payload, timeout=90)
                        if resp.status_code == 200:
                            raw_text = resp.text
                            Messenger.info(f"POST succeeded for {model}")
                    except Exception:
                        pass
                    
                    # Fallback to GET if POST failed
                    if not raw_text:
                        short_prompt = f"{system_prompt}\n\n{prompt}"[:2500]
                        encoded = urllib.parse.quote(short_prompt)
                        url = f"{self.get_url}{encoded}"
                        resp = requests.get(url, params={"model": model, "jsonMode": "true"}, timeout=90)
                        if resp.status_code == 200:
                            raw_text = resp.text
                            Messenger.info(f"GET succeeded for {model}")
                    
                    if not raw_text:
                        Messenger.warning(f"No response from {model}")
                        continue
                    
                    # Process response
                    content = self._unwrap_response(raw_text)
                    json_str = self._extract_scenes_json(content)
                    
                    result = schema.model_validate_json(json_str)
                    Messenger.success(f"✅ Parsed {model} response! Scenes: {len(result.scenes) if hasattr(result, 'scenes') else '?'}")
                    return result
                    
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                    Messenger.warning(f"Network error with {model}.")
                except Exception as e:
                    last_error = e
                    Messenger.warning(f"Error with {model}: {str(e)[:200]}")
                    if attempt >= 2:
                        break  # Next model after 3 tries
        
        Messenger.error("CRITICAL: All models failed.")
        raise last_error if last_error else RuntimeError("Failed to generate text")
