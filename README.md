# ARIA — Video Call AI

Real-time AI video call. ARIA sees your face, reads expressions, talks like a human.

## Features
- Always-on mic — continuous listening, never cuts off
- Reads your face every 3 seconds — reacts to your expressions
- Notices when you leave the frame
- Drives the conversation — doesn't wait silently
- Interruption support — speak while ARIA talks, she stops
- Persistent memory — remembers you across calls
- Real voice output via browser TTS

## Deploy to Railway (free)

1. Push this folder to a GitHub repo
2. Go to railway.app → New Project → Deploy from GitHub
3. Select your repo
4. Add environment variable: ANTHROPIC_API_KEY = your key
5. Deploy → get your URL → share with anyone!

## Local test
```
pip install flask flask-cors anthropic gunicorn
export ANTHROPIC_API_KEY=your_key_here
python app.py
```
Then open http://localhost:5000
