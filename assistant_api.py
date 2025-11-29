# assistant_api.py
# FastAPI assistant service: Chroma retrieval + FREE Groq LLM integration.

from fastapi import FastAPI, HTTPException, Request
import uuid
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os, time, json
from chromadb import Client

# --- GROQ LLM (FREE) ---
from groq import AsyncGroq

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    # Use provided key as default for demo
    groq_key = os.getenv("GROQ_API_KEY")
    print("INFO: Using default GROQ_API_KEY from code.")

groq_client = AsyncGroq(api_key=groq_key)

app = FastAPI(title='SankalpAI Assistant API')
@app.get("/logo")
async def logo():
    return FileResponse(r"C:/Users/Indira/.gemini/antigravity/brain/ac913dbf-c715-4789-8c25-c18fe25beef2/logo_image_1764322156257.png")


# -------- Chat UI --------
CHAT_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>SankalpAI Cyber Sankalp Assistant</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    /* Navy Blue Dark + Neon Glow + Glassmorphism */
    :root{
      --bg: #0a192f;
      --bg-gradient: linear-gradient(135deg, #0a192f 0%, #020c1b 100%);
      --panel: rgba(17, 34, 64, 0.75);
      --muted: #8892b0;
      --primary: #64ffda;   /* Neon Cyan */
      --secondary: #00f3ff; /* Bright Neon Blue */
      --border: rgba(100, 255, 218, 0.3);
      --bot-bg: rgba(255, 255, 255, 0.05);
      --user-bg: rgba(100, 255, 218, 0.15);
      --shadow: 0 10px 30px -10px rgba(2, 12, 27, 0.7);
      --glow: 0 0 10px rgba(100, 255, 218, 0.2);
      --font: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --maxw: 1000px;
      --text-main: #e6f1ff;
      --text-head: #ccd6f6;
    }
    html,body{height:100%;margin:0;background:var(--bg-gradient);font-family:var(--font);color:var(--text-main); overflow: hidden;}
    
    .container{
        display:flex;
        align-items:center;
        justify-content:center;
        padding:20px;
        height:100vh;
        box-sizing: border-box;
    }
    
    .panel{
        width:100%;
        max-width:var(--maxw);
        height: 90vh; /* Fixed height */
        background:var(--panel);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow:var(--shadow);
        border-radius:20px;
        overflow:hidden;
        border:1px solid var(--border);
        display: flex;
        flex-direction: column;
        position: relative;
    }
    
    /* Header */
    header{
        display:flex;
        align-items:center;
        gap:16px;
        padding:16px 24px;
        border-bottom:1px solid var(--border);
        background: rgba(10, 25, 47, 0.6);
        flex-shrink: 0;
    }
    header img.logo{
        width:48px;
        height:48px;
        border-radius:10px;
        object-fit:cover;
        border: 1px solid var(--primary);
        box-shadow: var(--glow);
    }
    .title{
        font-weight:700;
        font-size:20px;
        color: var(--text-head);
        letter-spacing: 0.5px;
        text-shadow: 0 0 5px rgba(100, 255, 218, 0.4);
    }
    .subtitle{
        font-size:13px;
        color:var(--primary);
        margin-top:4px;
        font-family: monospace;
    }
    .header-right{
        margin-left:auto;
        text-align:right;
        font-size:13px;
        color:var(--muted);
    }
    
    /* Layout */
    .layout{
        display:flex;
        gap:20px;
        padding:20px;
        flex: 1;
        overflow: hidden;
        min-height: 0;
    }
    .left{
        flex:1;
        min-width:320px;
        display:flex;
        flex-direction:column;
        height: 100%;
        min-height: 0;
    }
    .chat-area{
        flex:1;
        border-radius:12px;
        padding:20px;
        overflow-y:auto;
        background: rgba(2, 12, 27, 0.3);
        border:1px solid var(--border);
        scroll-behavior:smooth;
        margin-bottom: 16px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.2);
    }
    
    /* Scrollbar */
    .chat-area::-webkit-scrollbar { width: 8px; }
    .chat-area::-webkit-scrollbar-track { background: transparent; }
    .chat-area::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
    .chat-area::-webkit-scrollbar-thumb:hover { background: var(--primary); }

    .right{
        width:300px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    /* Sidebar Cards */
    .sidebar-card{
        background: rgba(17, 34, 64, 0.6);
        border:1px solid var(--border);
        padding:16px;
        border-radius:12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .sidebar-card h3 {
        margin: 0 0 12px 0;
        font-size: 14px;
        color: var(--primary);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Controls */
    .controls{
        display:flex;
        gap:12px;
        align-items:center;
        flex-shrink: 0;
    }
    input.msg-in{
        flex:1;
        padding:14px 16px;
        border:1px solid var(--border);
        border-radius:10px;
        font-size:15px;
        background: rgba(2, 12, 27, 0.5);
        color: var(--text-main);
        transition: all 0.2s;
    }
    input.msg-in:focus{
        outline: none;
        border-color: var(--primary);
        box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
    }
    input.msg-in::placeholder { color: var(--muted); }
    
    button.send{
        background: transparent;
        color: var(--primary);
        border: 1px solid var(--primary);
        padding: 12px 20px;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 0 10px rgba(100, 255, 218, 0.1);
    }
    button.send:hover{
        background: rgba(100, 255, 218, 0.1);
        box-shadow: 0 0 15px rgba(100, 255, 218, 0.3);
        transform: translateY(-1px);
    }
    button.ghost{
        background: transparent;
        border: 1px solid var(--muted);
        padding: 12px 16px;
        border-radius: 10px;
        cursor: pointer;
        color: var(--muted);
        transition: all 0.2s;
    }
    button.ghost:hover{
        border-color: var(--text-main);
        color: var(--text-main);
    }
    
    .tip{
        font-size:12px;
        color:var(--muted);
        margin-top:10px;
        flex-shrink: 0;
        text-align: center;
    }
    .tip strong { color: var(--primary); }
    
    footer{
        padding:12px 24px;
        border-top:1px solid var(--border);
        font-size:12px;
        color:var(--muted);
        background: rgba(10, 25, 47, 0.8);
        flex-shrink: 0;
        text-align: center;
    }
    
    /* Messages */
    .msg-row{display:flex;gap:14px;align-items:flex-start;margin:16px 0;}
    .avatar{
        width:42px;
        height:42px;
        border-radius:10px;
        background: rgba(17, 34, 64, 1);
        display:flex;
        align-items:center;
        justify-content:center;
        color: var(--primary);
        font-weight:700;
        border:1px solid var(--border);
        flex-shrink:0;
        box-shadow: var(--glow);
    }
    .avatar img{width:100%;height:100%;border-radius:10px;object-fit:cover}
    
    .bubble{
        max-width:80%;
        padding:14px 18px;
        border-radius:12px;
        line-height:1.5;
        font-size:15px;
        border:1px solid var(--border);
        color: var(--text-main);
        position: relative;
    }
    .who{font-size:12px;color:var(--primary);margin-bottom:6px; font-weight: 600;}
    
    .bot .bubble{
        background: var(--bot-bg);
        border-top-left-radius: 2px;
    }
    .user-row{justify-content:flex-end}
    .user-row .bubble{
        background: var(--user-bg);
        border-color: var(--primary);
        color: #fff;
        border-top-right-radius: 2px;
    }
    .user-row .avatar{
        background: var(--primary);
        color: #0a192f;
        border-color: var(--primary);
    }
    .time{display:block;font-size:11px;color:var(--muted);margin-top:8px; text-align: right;}
    
    /* Typing Indicator */
    .typing-row{display:flex;gap:14px;align-items:flex-start;margin:16px 0;}
    .typing-bubble{
        padding:12px 16px;
        border-radius:18px;
        background: var(--bot-bg);
        border:1px solid var(--border);
        display:inline-flex;
        align-items:center;
        gap:10px;
    }
    .dot{width:6px;height:6px;border-radius:50%;background:var(--primary);opacity:0.4;animation:dot 1.2s infinite}
    .dot.d2{animation-delay:.15s}.dot.d3{animation-delay:.3s}
    @keyframes dot{0%{transform:translateY(4px);opacity:.4}40%{transform:translateY(0);opacity:1}80%{transform:translateY(-2px);opacity:.4}100%{transform:translateY(4px);opacity:.4}}
    
    /* Animations */
    .fade{animation:fadeIn .3s ease both}
    @keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
    
    /* Responsive */
    @media(max-width:880px){
        .layout{flex-direction:column; gap: 10px;}
        .right{width:100%; height: auto; max-height: 200px;}
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="panel" role="main" aria-label="SankalpAI chat panel">
      <header>
        <!-- logo served via /logo -->
        <img class="logo" src="/logo" alt="SankalpAI logo" onerror="this.onerror=null; this.src=''"/>
        <div>
          <div class="title">SankalpAI Cyber Sankalp Assistant</div>
          <div class="subtitle">SECURE â€¢ INTELLIGENT â€¢ FAST</div>
        </div>
        <div class="header-right">
          <div>Local Demo</div>
          <div style="margin-top:6px;color:var(--muted)">User: <strong style="color:var(--primary)">indira</strong></div>
        </div>
      </header>

      <div class="layout">
        <div class="left">
          <div id="chatArea" class="chat-area" aria-live="polite">
            <!-- welcome -->
            <div class="msg-row bot fade" id="welcomeRow">
              <div class="avatar" aria-hidden="true">S</div>
              <div class="bubble">
                <div class="who">SankalpAI</div>
                <div>Hello. I am your advanced cyber security assistant. I can detect vulnerabilities, execute scans, and manage tickets.</div>
                <div style="margin-top:8px; font-size:13px; color:var(--muted)">Try asking: <em style="color:var(--text-head)">"Analyze the risk level of device-0."</em></div>
                <span class="time">System Ready</span>
              </div>
            </div>
          </div>

          <div class="controls" role="region" aria-label="Chat controls">
            <input id="inputMain" class="msg-in" type="text" placeholder="Enter command or query..." aria-label="Chat input" />
            <button id="btnSend" class="send" aria-label="Send message">SEND</button>
            <button id="btnClear" class="ghost" aria-label="Clear chat">CLEAR</button>
          </div>

          <div class="tip"><strong>Tip:</strong> Provide specific IDs (e.g., <code>device-0</code>) for precise analysis.</div>
        </div>

        <aside class="right">
          <div class="sidebar-card">
            <h3>Latest Sources</h3>
            <div id="sources" style="font-size:13px; color:var(--muted)">No data retrieved.</div>
          </div>

          <div class="sidebar-card">
            <h3>Quick Actions</h3>
            <div style="display:flex;gap:10px; flex-wrap: wrap;">
              <button id="runScanBtn" class="send" style="flex:1; background: rgba(100, 255, 218, 0.1);">RUN SCAN</button>
              <button id="createTicketBtn" class="ghost" style="flex:1">TICKET</button>
            </div>
            <div id="actionStatus" style="margin-top:10px; font-size:12px; color:var(--primary)"></div>
          </div>

          <div class="sidebar-card" style="font-size:12px; color:var(--muted)">
            <div><strong>SYSTEM:</strong> ONLINE</div>
            <div style="margin-top:6px"><strong>MODEL:</strong> Llama-3.1-8b-instant</div>
            <div style="margin-top:6px"><strong>MODE:</strong> RAG ENABLED</div>
          </div>
        </aside>
      </div>

      <footer>SankalpAI v2.0 â€” Secure Environment. Local Execution.</footer>
    </div>
  </div>

<script>
/* --- Utility for appending messages (supports avatarUrl in metadata) --- */
const chatArea = document.getElementById('chatArea');
const inputMain = document.getElementById('inputMain');
const btnSend = document.getElementById('btnSend');
const btnClear = document.getElementById('btnClear');
const runScanBtn = document.getElementById('runScanBtn');
const createTicketBtn = document.getElementById('createTicketBtn');
const sourcesEl = document.getElementById('sources');
const actionStatus = document.getElementById('actionStatus');

function createAvatarElement(avatarUrl, who){
  const av = document.createElement('div'); av.className='avatar';
  if(avatarUrl){
    const img = document.createElement('img'); img.src = avatarUrl; img.alt = who;
    img.onerror = ()=> { img.style.display='none'; av.textContent = who.charAt(0).toUpperCase(); };
    av.appendChild(img);
  } else {
    av.textContent = who.charAt(0).toUpperCase();
  }
  return av;
}

function appendMessage(who, text, opts = {}){
  const row = document.createElement('div'); row.className = 'msg-row ' + (who==='user' ? 'user-row' : 'bot'); row.classList.add('fade');
  const avatar = createAvatarElement(opts.avatarUrl, who);
  const bubble = document.createElement('div'); bubble.className = 'bubble';
  const whoLine = document.createElement('div'); whoLine.className='who'; whoLine.innerHTML = '<strong>' + (opts.displayName || who) + '</strong>';
  bubble.appendChild(whoLine);
  const content = document.createElement('div'); content.innerHTML = (text||'').replace(/\\n/g,'<br/>'); bubble.appendChild(content);
  if(opts.time){ const t = document.createElement('span'); t.className='time'; t.textContent = opts.time; bubble.appendChild(t); }
  if(who==='user'){ row.appendChild(bubble); row.appendChild(avatar); } else { row.appendChild(avatar); row.appendChild(bubble); }
  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight;
  return row;
}

/* typing indicator (WhatsApp-style) */
function showTyping(){
  const tr = document.createElement('div'); tr.className='typing-row'; tr.id='typingRow';
  const av = document.createElement('div'); av.className='avatar'; av.textContent='S';
  const tb = document.createElement('div'); tb.className='typing-bubble';
  const who = document.createElement('div'); who.className='who'; who.innerHTML = '<strong>SankalpAI</strong>';
  const dots = document.createElement('div'); dots.style.display='flex'; dots.style.gap='6px';
  const d1 = document.createElement('div'); d1.className='dot d1';
  const d2 = document.createElement('div'); d2.className='dot d2';
  const d3 = document.createElement('div'); d3.className='dot d3';
  dots.appendChild(d1); dots.appendChild(d2); dots.appendChild(d3);
  tb.appendChild(who); tb.appendChild(dots); tr.appendChild(av); tr.appendChild(tb);
  chatArea.appendChild(tr); chatArea.scrollTop = chatArea.scrollHeight;
  return tr;
}
function hideTyping(){ const el = document.getElementById('typingRow'); if(el) el.remove(); }

/* backend caller */
async function callChatAPI(message, deviceId='device-0'){
  appendMessage('user', message, {time: new Date().toLocaleTimeString()});
  inputMain.value='';
  const typingEl = showTyping();
  try{
    const payload = { user_id: 'indira', message: message, device_id: deviceId };
    const res = await fetch('/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const j = await res.json();
    hideTyping();
    if(j && j.response){
      appendMessage('bot', j.response, {time: new Date().toLocaleTimeString(), displayName: 'SankalpAI'});
    } else {
      appendMessage('bot', '[No response from LLM]', {time: new Date().toLocaleTimeString()});
    }
    // update sources
    if(j && j.sources && j.sources.length){
      sourcesEl.innerHTML = j.sources.slice(0,6).map(s => '<div><strong>' + (s.device_id||s.id||'device') + '</strong> â€¢ ' + (s.scan_ts||'') + '</div>').join('');
    } else {
      sourcesEl.innerHTML = 'No retrieved sources.';
    }
  } catch(err){
    hideTyping();
    appendMessage('bot', 'Error: ' + err.toString(), {time: new Date().toLocaleTimeString()});
  }
}

/* wire events */
btnSend.addEventListener('click', ()=> { if(inputMain.value.trim()) callChatAPI(inputMain.value.trim()); });
inputMain.addEventListener('keydown', (e)=> { if(e.key==='Enter' && inputMain.value.trim()) callChatAPI(inputMain.value.trim()); });
btnClear.addEventListener('click', ()=> { chatArea.innerHTML = ''; sourcesEl.innerHTML = 'No retrieved sources.'; });

/* Run Scan and Create Ticket wiring -- calls working backend endpoints and shows result */
runScanBtn.addEventListener('click', async ()=>{
  runScanBtn.disabled = true;
  runScanBtn.textContent = 'Scheduling...';
  try{
    const r = await fetch('/action/run_scan', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({})});
    const j = await r.json();
    actionStatus.textContent = 'Scan scheduled: ' + (j.job_id || '[unknown]');
    appendMessage('bot', `Scan scheduled: ${j.job_id || '[unknown]'}`, {time: new Date().toLocaleTimeString()});
  } catch(e){
    actionStatus.textContent = 'Scan failed';
    appendMessage('bot', 'Run scan failed: ' + e.toString(), {time: new Date().toLocaleTimeString()});
  } finally { runScanBtn.disabled=false; runScanBtn.textContent='Run Scan'; }
});

createTicketBtn.addEventListener('click', async ()=>{
  createTicketBtn.disabled = true;
  createTicketBtn.textContent = 'Creating...';
  try{
    const r = await fetch('/action/create_ticket', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({})});
    const j = await r.json();
    actionStatus.textContent = 'Ticket created: ' + (j.ticket_id || '[unknown]');
    appendMessage('bot', `Ticket created: ${j.ticket_id || '[unknown]'}`, {time: new Date().toLocaleTimeString()});
  } catch(e){
    actionStatus.textContent = 'Ticket creation failed';
    appendMessage('bot', 'Ticket creation failed: ' + e.toString(), {time: new Date().toLocaleTimeString()});
  } finally { createTicketBtn.disabled=false; createTicketBtn.textContent='Create Ticket'; }
});

/* Optional: if you plan to include avatar URLs in your RAG metadata, include metadata.avatar_url = "/logo" or actual image URL.
   Examples of extra metadata that improves answers:
   device_id, device_model, firmware_version, open_ports (array), default_password_status (true/false),
   last_scan_ts, known_cves (list), manufacturer, location, external_ip_detected (bool)
*/

/* END of script */
</script>
</body>
</html>
"""






@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(CHAT_HTML)

@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui():
    return HTMLResponse(CHAT_HTML)

# -------- ChromaDB --------
client = Client()
try:
    col = client.get_collection("cctv_devices")
except:
    col = client.create_collection(name="cctv_devices")

class ChatRequest(BaseModel):
    user_id: str
    message: str
    device_id: str = None

# -------- Retrieval --------
def retrieve_context(query, device_id=None, k=4):
    try:
        if device_id:
            result = col.query(query_texts=[query], n_results=k, where={"device_id": device_id})
        else:
            result = col.query(query_texts=[query], n_results=k)
    except:
        return []

    docs = []
    for doc, meta in zip(result.get("documents", [[]])[0], result.get("metadatas", [[]])[0]):
        docs.append({"content": doc, "metadata": meta})

    return docs

# -------- FREE GROQ LLM --------
async def run_llm(system_prompt, user_prompt, max_tokens=200, temperature=0.1):
# The GROQ_API_KEY is already validated at startup; no need to reâ€‘check here.

    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",   # or your chosen Groq model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
    
        # safe extraction of text from SDK response (handles object or dict)
        choice = None
        choices = getattr(completion, "choices", None) or completion.get("choices", [])
        if choices:
            choice = choices[0]
        else:
            raise RuntimeError("No choices returned from LLM")

        # message may be an object with .content or a dict with ['message']['content']
        message = getattr(choice, "message", None) or choice.get("message", {})
        # message might be object -> try .content, else dict -> try ['content'] or ['message']['content']
        content = None
        if hasattr(message, "content"):
            content = message.content
        elif isinstance(message, dict) and "content" in message:
            content = message["content"]
        elif isinstance(choice, dict) and "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
            content = choice["message"]["content"]

        if content is None:
            # fallback to full response string
            return str(completion)

        return content

    except Exception as e:
        raise RuntimeError(f"GROQ request failed: {e}")


# -------- Chat endpoint --------
@app.post("/chat")
async def chat(req: ChatRequest):

    ctx = retrieve_context(req.message, device_id=req.device_id, k=4)
    retrieved_text = "\n\n".join(
        [f"[{d['metadata'].get('device_id')}] {d['content']}" for d in ctx]
    ) if ctx else ""

    system_prompt = (
        "You are SecAI, an assistant for CCTV vulnerability analysis. "
        "Start with a 1-line answer, then show evidence lines. "
        "If context missing, say you cannot confirm and suggest next steps."
    )

    user_prompt = f"Context:\n{retrieved_text}\n\nUser: {req.message}\nAssistant:"

    try:
        response = await run_llm(system_prompt, user_prompt)
    except Exception as e:
        return {"response": f"[LLM error] {str(e)}", "sources": ctx}

    return {"response": response, "sources": ctx}

# Global inâ€‘memory store for scan jobs
scan_jobs: dict[str, dict] = {}

# -------- Dummy endpoints --------
@app.post("/action/run_scan")
async def run_scan(payload: dict):
    # Generate a deterministic UUIDâ€‘based job ID
    job_id = f"scan-{uuid.uuid4().hex[:8]}"
    # Store job info in a simple inâ€‘memory dict (could be replaced by a DB later)
    scan_jobs[job_id] = {"status": "scheduled", "created": time.time()}
    return {"job_id": job_id, "status": "scheduled"}

@app.post("/action/create_ticket")
async def create_ticket(payload: dict):
    return {"ticket_id": f"TICKET-{int(time.time())}", "status": "created"}

