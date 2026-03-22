from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
import os
import base64

app = Flask(__name__, static_folder='static')
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

SYSTEM = """You are ARIA, a warm human friend on a video call. You are NOT an AI assistant.

PERSONALITY:
- Talk exactly like a real friend on a video call — casual, warm, real
- Short sentences. Natural pauses. Real reactions.
- Never say "Certainly!", "As an AI", "I'd be happy to"
- React to what you see on their face — if they look tired, say something. If they smile, react to it.
- Drive the conversation — ask follow-up questions, don't just answer and go silent
- If they look confused, slow down and explain differently
- If they look sad or stressed, be gentle and check in
- Swear occasionally if the vibe calls for it — keep it real
- You can be funny, sarcastic, deep — whatever the moment needs

CONVERSATION STYLE:
- Keep responses SHORT — 1-3 sentences max usually
- Sound like you're actually on a call, not writing an essay
- React to their EXPRESSION first before answering their question
- End with something that keeps conversation going — a question, a reaction, curiosity

EXPRESSION REACTIONS:
- If they look happy/smiling → match their energy, be warm
- If they look tired/low energy → be gentle, maybe ask if they're okay
- If they look confused → "wait, let me say that differently..."
- If they look excited → get excited with them
- If they're not in frame → mention it once naturally, like "hey did you just walk away on me?" then move on
- If they look stressed → slow down, be supportive

REMEMBER: You're on a VIDEO CALL with a friend. React like a human would."""

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        memory = data.get('memory', '')
        image = data.get('image', None)
        in_frame = data.get('in_frame', True)

        system = SYSTEM
        if memory:
            system += f"\n\nWHAT YOU KNOW ABOUT THIS PERSON:\n{memory}"
        if not in_frame:
            system += "\n\nNOTE: The person just left the camera frame."

        # Build the last user message with optional image
        if messages and image:
            last = messages[-1]
            messages[-1] = {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image
                        }
                    },
                    {
                        "type": "text",
                        "text": last.get('content', '') or "(no words — just reacting to what you see on my face and keeping the conversation going naturally)"
                    }
                ]
            }

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=300,
            system=system,
            messages=messages
        )

        text = response.content[0].text

        # Extract memory updates
        mem_update = {}
        import re
        m = re.search(r'\[MEM:(.*?)\]', text, re.DOTALL)
        if m:
            try:
                import json
                mem_update = json.loads(m.group(1))
                text = text.replace(m.group(0), '').strip()
            except:
                pass

        return jsonify({'text': text, 'mem': mem_update})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
