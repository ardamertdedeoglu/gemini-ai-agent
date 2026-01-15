import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import available_functions, call_function
from prompts import system_prompt

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if api_key is None:
    raise RuntimeError("API key cannot be found")

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

for _ in range(20):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
    if response.candidates is not None:
        if len(response.candidates) != 0:
            for candidate in response.candidates:
                if candidate.content is not None:
                    messages.append(candidate.content)

    function_results = []
    if response.usage_metadata is not None:
        if response.function_calls is not None:
            for function_call in response.function_calls:
                function_call_result = call_function(function_call)
                if function_call_result.parts is not None:
                    if len(function_call_result.parts) == 0:
                        raise Exception("empty parts")
                    if function_call_result.parts[0].function_response is None:
                        raise Exception("Empty function response")
                    if function_call_result.parts[0].function_response.response is None:
                        raise Exception("Empty response dict")
                    function_results.append(function_call_result.parts[0])
                    messages.append(types.Content(role="user", parts=function_results))
                else:
                    raise Exception("empty result")
                if args.verbose:
                    print(f"User prompt: {args.user_prompt}")
                    print(
                        f"Prompt tokens: {response.usage_metadata.prompt_token_count}"
                    )
                    print(
                        f"Response tokens: {response.usage_metadata.candidates_token_count}"
                    )
                    print(
                        f"-> {function_call_result.parts[0].function_response.response}"
                    )
        else:
            print(response.text)
            break
    else:
        raise RuntimeError("Usage Metadata cannot be found")
