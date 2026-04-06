import os

with open("assistant_api.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Extract HTML
start_marker = 'CHAT_HTML = """\n'
end_marker = '"""\n'
start_idx = content.find(start_marker)

if start_idx != -1:
    end_idx = content.find(end_marker, start_idx + len(start_marker))
    html_content = content[start_idx + len(start_marker):end_idx]
    
    os.makedirs("static", exist_ok=True)
    with open("static/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Remove CHAT_HTML definition from content
    content = content[:start_idx] + "\n" + content[end_idx + len(end_marker):]
    print("Extracted CHAT_HTML to static/index.html")

# 2. Add logging imports and configure
if "import logging" not in content:
    content = content.replace("from cachetools import TTLCache\n", 
                              "from cachetools import TTLCache\nimport logging\n\nlogging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')\nlogger = logging.getLogger('secai')\n")
    print("Injected logging config")

# 3. Replace print -> logger.info
content = content.replace('print(f"Cache HIT for query: {req.message}")', 'logger.info(f"Cache HIT for query: {req.message}")')
content = content.replace('print(f"Retrieval Error: {e}")', 'logger.error(f"Retrieval Error: {e}")')
content = content.replace('return f"[LLM Error] {str(e)}"', 'logger.error(f"LLM Error: {e}"); return f"[LLM Error] {str(e)}"')

# 4. Modify root endpoint
root_old = '''@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(CHAT_HTML)'''
root_new = '''@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("static/index.html")'''
if root_old in content:
    content = content.replace(root_old, root_new)
    print("Modified root endpoint")

with open("assistant_api.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
