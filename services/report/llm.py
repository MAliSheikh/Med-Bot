import time
import re
from openai import OpenAI, RateLimitError, APIStatusError
from core import config
from services.report.prompt import get_guardrail_prompt


# --- Model Selection ---
# Uncomment the model you wish to use.
# Rate Limits: RPM (Requests Per Minute), RPD (Requests Per Day), TPM (Tokens Per Minute), TPD (Tokens Per Day)

# MODEL = "allam-2-7b"                                  # RPM: 30, RPD: 7K, TPM: 6K, TPD: 500K
# MODEL = "canopylabs/orpheus-arabic-saudi"             # RPM: 10, RPD: 100, TPM: 1.2K, TPD: 3.6K
# MODEL = "canopylabs/orpheus-v1-english"               # RPM: 10, RPD: 100, TPM: 1.2K, TPD: 3.6K
# MODEL = "groq/compound"                               # RPM: 30, RPD: 250, TPM: 70K
# MODEL = "groq/compound-mini"                          # RPM: 30, RPD: 250, TPM: 70K
# MODEL = "llama-3.1-8b-instant"                        # RPM: 30, RPD: 14.4K, TPM: 6K, TPD: 500K
MODEL = "llama-3.3-70b-versatile"                     # RPM: 30, RPD: 1K, TPM: 12K, TPD: 100K
# MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct" # RPM: 30, RPD: 1K, TPM: 6K, TPD: 500K
# MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"   # RPM: 30, RPD: 1K, TPM: 30K, TPD: 500K
# MODEL = "meta-llama/llama-guard-4-12b"                # RPM: 30, RPD: 14.4K, TPM: 15K, TPD: 500K
# MODEL = "meta-llama/llama-prompt-guard-2-22m"         # RPM: 30, RPD: 14.4K, TPM: 15K, TPD: 500K
# MODEL = "meta-llama/llama-prompt-guard-2-86m"         # RPM: 30, RPD: 14.4K, TPM: 15K, TPD: 500K
# MODEL = "moonshotai/kimi-k2-instruct"                 # RPM: 60, RPD: 1K, TPM: 10K, TPD: 300K
# MODEL = "moonshotai/kimi-k2-instruct-0905"            # RPM: 60, RPD: 1K, TPM: 10K, TPD: 300K
# MODEL = "openai/gpt-oss-120b"                         # RPM: 30, RPD: 1K, TPM: 8K, TPD: 200K
# MODEL = "openai/gpt-oss-20b"                          # RPM: 30, RPD: 1K, TPM: 8K, TPD: 200K
# MODEL = "openai/gpt-oss-safeguard-20b"                # RPM: 30, RPD: 1K, TPM: 8K, TPD: 200K
# MODEL = "qwen/qwen3-32b"                              # RPM: 60, RPD: 1K, TPM: 6K, TPD: 500K

# Initialize OpenAI client for Groq
client = OpenAI(
    api_key=config.GROQ_API_KEY,
    base_url=config.GROQ_API_URL
)

def parse_rate_limit_headers(headers):
    """
    Parses rate limit headers to determine wait time.
    """
    # 1. Check retry-after (seconds)
    retry_after = headers.get("retry-after")
    if retry_after:
        return float(retry_after)
    
    # 2. Check specific reset times
    # Format examples: "2m59.56s", "7.66s"
    reset_requests = headers.get("x-ratelimit-reset-requests")
    reset_tokens = headers.get("x-ratelimit-reset-tokens")
    
    def parse_duration(duration_str):
        if not duration_str:
            return 0
        try:
            # Match minutes and seconds
            match = re.match(r'(?:(\d+)m)?([\d.]+)s', duration_str)
            if match:
                minutes = int(match.group(1) or 0)
                seconds = float(match.group(2) or 0)
                return (minutes * 60) + seconds
        except Exception:
            pass
        return 0

    wait_req = parse_duration(reset_requests)
    wait_tok = parse_duration(reset_tokens)
    
    return max(wait_req, wait_tok)

def analyze_text(text, user_info=None, past_reports=None):
    prompt = get_guardrail_prompt(text, user_info=user_info, past_reports=past_reports)
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=MODEL,
                temperature=0.1,
                max_tokens=1000,
            )
            return {"analysis": chat_completion.choices[0].message.content}
            
        except RateLimitError as e:
            print(f"Rate limit hit: {e}")
            wait_time = parse_rate_limit_headers(e.response.headers) if e.response else 0
            
            if wait_time == 0:
                wait_time = 2 ** attempt # Exponential backoff if no header
            
            print(f"Waiting {wait_time:.2f}s before retrying...")
            time.sleep(wait_time)
            
        except APIStatusError as e:
            if e.status_code == 503:
                print("Service unavailable (503). Waiting 10s...")
                time.sleep(10)
            else:
                print(f"API Error: {e}")
                break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
            
    return {"error": "Failed to analyze text"}