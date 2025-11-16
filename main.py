import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import system_prompt
from config import MAX_ITERATIONS
from call_function import available_functions, call_function


def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    # args = []
    # for arg in sys.argv[1:]:
    #     if not arg.startswith("--"):
    #         args.append(arg)

    # if not args:
    #     print("AI Code Assistant")
    #     print('Usage: python main.py "your prompt here" [--verbose]')
    #     print('Example: python main.py "How do I fix the calculator?"')
    #     sys.exit(1)

    print("Before the ride questionnaire")
    age = input("Enter your age: ")
    sex = input("Enter your sex: ")
    weight = input("Enter your weight: ")
    height = input("Enter your height: ")
    rider = f"Your age is {age}, your sex is {sex}, your weight is {weight}, your height is {height}"
    
    print("Let's go on a hypothetical ride")
    distance = input("Enter the distance of the ride: ")
    elevation_gain = input("Enter the elevation gain of the ride: ")
    ride = f"The distance of the ride is {distance}, the elevation gain is {elevation_gain}"

    # Generate the model result
    model_result = "1000 kcal"

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(model_result)

    # if verbose:
    #     print(f'User prompt: {user_prompt}\n')

    messages = [
        types.Content(
            role="user",
            parts=[types.Part(text=user_prompt)]
        ),
    ]

    for _ in range(MAX_ITERATIONS):
        try:
            final_response = generate_content(client, messages, verbose)
            if final_response:
                print("Final response:")
                print(final_response)
                return
        except Exception as e:
            print(f'Error in generate content: {e}')

    print(f'Maximum iterations ({MAX_ITERATIONS}) reached.')
    sys.exit(1)


def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
        ),
    )
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    if not response.function_calls:
        return response.text

    function_call_responses = []
    for function_call_part in response.function_calls:
        function_call_result = call_function(function_call_part, verbose)
        if (
            not function_call_result.parts
            or not function_call_result.parts[0].function_response.response
        ):
            raise Exception("Error: empty function call result")
        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")
        function_call_responses.append(function_call_result.parts[0])

        if not function_call_responses:
            raise Exception("Error: no function call responses generated")

    messages.append(types.Content(
        role="user",
        parts=function_call_responses,
    ))


if __name__ == "__main__":
    main()
