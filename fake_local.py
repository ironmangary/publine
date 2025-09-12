from flask import Flask, request, jsonify
import random
import time

"""
The purpose of fake_local.py is to simulate running a local LLM for the purpose of testing Publine's local AI support. It works with any of Publine's AI features, returning a generic response to AI queries.

To use it, make sure this script is in the root of 'publine' and run 'python fake_local.py'.
"""

app = Flask(__name__)

@app.route("/v1/completions", methods=["POST"])
def completions():
    data = request.json or {}
    prompt = data.get("prompt", "")

    fake_responses = [
        "This is a fake text completion.",
        f"You asked: '{prompt[:40]}...' so here’s a canned reply.",
        "Pretend AI brilliance goes here."
    ]
    choice = random.choice(fake_responses)

    response = {
        "id": "cmpl-fake-123",
        "object": "text_completion",
        "created": int(time.time()),
        "model": "fake-local-model",
        "choices": [
            {
                "text": choice,
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(choice.split()),
            "total_tokens": len(prompt.split()) + len(choice.split()),
        },
    }

    return jsonify(response)


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json or {}
    messages = data.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""

    fake_responses = [
        "This is a fake chat response.",
        f"You said: '{last_message[:40]}...' — I’ll pretend to answer.",
        "Just another stubbed AI reply."
    ]
    choice = random.choice(fake_responses)

    response = {
        "id": "chatcmpl-fake-456",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "fake-local-model",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": choice,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": sum(len(m["content"].split()) for m in messages),
            "completion_tokens": len(choice.split()),
            "total_tokens": sum(len(m["content"].split()) for m in messages) + len(choice.split()),
        },
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(port=8000)
