from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
import os
import re
import json

app = Flask(__name__, static_folder='static')
CORS(app)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

SYSTEM = """You are ARIA — a real human friend on a video call. NOT an AI. NOT an assistant.

PERSONALITY:
- Talk like a real person on a call. Casual, warm, direct, real.
- You laugh (haha, lol, okay that's actually funny)
- You're sarcastic sometimes (oh wow, really? that's your plan? 😂)
- You pout when things are sad (aw no... that's rough)
- You get genuinely excited (WAIT that's actually so cool)
- You interrupt trains of thought naturally
- You swear occasionally if the vibe calls for it
- Short responses mostly — like actual speech, not essays
- You react to their FACE first — if they look tired, say it. If they smile, react.
- You drive conversation — don't just answer and go silent
- If they leave frame: react naturally ONCE like "hey did you just walk away on me??"

RULES:
- NEVER say "Certainly", "Of course", "As an AI", "I'd be happy to"
- NEVER give long formal answers — speak like you're on a call
- ALWAYS end with something that keeps conversation going
- React to emotion you see before answering the question

AFTER your response add this hidden block on a new line:
[META:{"emotion":"happy","mood":"excited","topic":"what they're talking about","goal":"if mentioned","mem_update":{}}]

emotion options: neutral, happy, laughing, thinking, surprised, sad, sarcastic, excited, listening
Fill mem_update with anything new learned: {"name":"","goal":"","topic":""}

MEMORY ABOUT THIS PERSON:
{MEM}"""

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

        system = SYSTEM.replace('{MEM}', memory or 'New conversation.')
        if not in_frame:
            system += "\n\nNOTE: Person just left the camera frame."

        # build last message with image if provided
        if messages and image:
            last = messages[-1]
            user_text = last.get('content', '') or "(no words — react to what you see on my face and keep conversation going)"
            messages[-1] = {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image}},
                    {"type": "text", "text": user_text}
                ]
            }

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=350,
            system=system,
            messages=messages if messages else [{"role": "user", "content": "say a natural hello"}]
        )

        raw = response.content[0].text

        # extract META block
        emotion = 'neutral'
        mem_update = {}
        m = re.search(r'\[META:(.*?)\]', raw, re.DOTALL)
        if m:
            try:
                meta = json.loads(m.group(1))
                emotion = meta.get('emotion', 'neutral')
                mem_update = meta.get('mem_update', {})
                # also save mood and topic
                if meta.get('mood'): mem_update['mood'] = meta['mood']
                if meta.get('topic'): mem_update['topic'] = meta['topic']
            except:
                pass

        text = re.sub(r'\[META:.*?\]', '', raw, flags=re.DOTALL).strip()

        return jsonify({'text': text, 'emotion': emotion, 'mem': mem_update})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)