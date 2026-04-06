
import os

file_path = r"c:\Users\Indira\Downloads\SankalpAI-Cyber-Sankalp-Assistant-main\SankalpAI-Cyber-Sankalp-Assistant-main\assistant_api.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_until = -1

for i, line in enumerate(lines):
    if i <= skip_until:
        continue
    
    # Update ChatRequest
    if "class ChatRequest(BaseModel):" in line:
        new_lines.append("class ChatRequest(BaseModel):\n")
        new_lines.append("    user_id: str\n")
        new_lines.append("    message: str\n")
        new_lines.append("    device_id: Optional[str] = None\n")
        new_lines.append("    image_data: Optional[str] = None\n")
        # Skip until the empty line or retrieval comment
        j = i + 1
        while j < len(lines) and ("user_id" in lines[j] or "message" in lines[j] or "device_id" in lines[j]):
            j += 1
        skip_until = j - 1
        continue

    # Update chat endpoint logic
    if "system_prompt = (" in line and i > 730: # Look for the system_prompt block in the chat endpoint
        new_lines.append("    system_prompt = (\n")
        new_lines.append("        \"You are SecAI, an advanced assistant for CCTV vulnerability analysis and cyber security. \"\n")
        new_lines.append("        \"Provide thorough and helpful responses based on the provided context. \"\n")
        new_lines.append("        \"If you find CVE information, explain the vulnerability, its severity, and the remediation steps in detail. \"\n")
        new_lines.append("        \"If context is missing, say you cannot confirm specific details but provide general best practices.\"\n")
        new_lines.append("    )\n")
        new_lines.append("    if req.image_data:\n")
        new_lines.append("        system_prompt += (\n")
        new_lines.append("            \" You are also provided with an image. \"\n")
        new_lines.append("            \"Analyze the image visually for security issues, errors, or anomalies and combine this with your text context.\"\n")
        new_lines.append("        )\n\n")
        new_lines.append("    user_prompt = f\"Context:\\n{retrieved_text}\\n\\nUser: {req.message}\\nAssistant:\"\n\n")
        new_lines.append("    try:\n")
        new_lines.append("        response = await run_llm(system_prompt, user_prompt, image_data=req.image_data)\n")
        
        # Skip original system_prompt and run_llm call
        j = i + 1
        while j < len(lines) and "response = await run_llm" not in lines[j]:
            j += 1
        skip_until = j
        continue
    
    new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Update successful")
