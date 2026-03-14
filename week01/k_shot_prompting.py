import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
# NOTE: The average success rate: 33%
YOUR_SYSTEM_PROMPT = """
Reverse the order of letters in a word.

## Definition

Reversing means reading the letters from the last letter to the first letter.

## Example

Example:
word: http
letters: h t t p
last-to-first: p t t h
answer: ptth

Example:
word: status
letters: s t a t u s
last-to-first: s u t a t s
answer: sutats

Example:
word: httpstatus
letters: h t t p s t a t u s
last-to-first: s u t a t s p t t h

## Guidelines
- The first char of *answer* should be equal to the last char of *word*.
- The last char of *answer* should be equal to the first char of *word*.
- IGNORE the word semantic and just collect the characters from last to first.
"""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

def calculate_success_rate(system_prompt: str, num_trials: int):
    cnt = 0
    for idx in range(num_trials):
        print(f"Running test {idx + 1} of {num_trials}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            cnt += 1
    print(f"Success Rate: {cnt / num_trials:%}")

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
    # calculate_success_rate(YOUR_SYSTEM_PROMPT, 100)
