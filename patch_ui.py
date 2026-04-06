
import os

file_path = r"c:\Users\Indira\Downloads\SankalpAI-Cyber-Sankalp-Assistant-main\SankalpAI-Cyber-Sankalp-Assistant-main\assistant_api.py"

with open(file_path, 'r', encoding='utf-8') as f:
    full_content = f.read()

# 1. Add CSS for image preview and upload button
css_anchor = "    input:checked + .slider:before { transform: translateX(20px); background-color: var(--primary); }"
new_css = """
    input:checked + .slider:before { transform: translateX(20px); background-color: var(--primary); }

    /* Image Preview */
    .img-preview-container {
        display: none;
        position: relative;
        margin-bottom: 15px;
        max-width: 150px;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid var(--primary);
    }
    .img-preview-container img {
        width: 100%;
        display: block;
    }
    .img-preview-container .remove-img {
        position: absolute;
        top: 2px;
        right: 2px;
        background: rgba(0,0,0,0.6);
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 12px;
        font-weight: bold;
    }
    .upload-btn {
        background: transparent;
        border: 1px solid var(--muted);
        color: var(--muted);
        border-radius: 50%;
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 18px;
        flex-shrink: 0;
    }
    .upload-btn:hover {
        border-color: var(--primary);
        color: var(--primary);
        background: rgba(100, 255, 218, 0.05);
    }

    /* Embedded image in chat bubbles */
    .bubble img {
        max-width: 100%;
        border-radius: 8px;
        margin-top: 10px;
        border: 1px solid rgba(100, 255, 218, 0.2);
    }
"""
full_content = full_content.replace(css_anchor, new_css)

# 2. Add Image Upload Controls in HTML
html_anchor = '            <input id="inputMain" class="msg-in" type="text" placeholder="Enter command or query..." aria-label="Chat input" />'
new_html = """
          <div id="imgPreviewContainer" class="img-preview-container">
            <span class="remove-img" id="removeImgBtn">&times;</span>
            <img id="imgPreview" src="" alt="preview" />
          </div>

          <div class="controls" role="region" aria-label="Chat controls">
            <input type="file" id="fileInput" accept="image/*" style="display:none" />
            <button id="btnUpload" class="upload-btn" title="Upload Image" aria-label="Upload image">🖼️</button>
            <input id="inputMain" class="msg-in" type="text" placeholder="Enter command or query..." aria-label="Chat input" />
"""
full_content = full_content.replace(html_anchor, new_html)

# 3. Update JavaScript logic
# Add variables
js_vars_anchor = "const voiceIndicator = document.getElementById('voiceIndicator');"
new_js_vars = """const voiceIndicator = document.getElementById('voiceIndicator');
const fileInput = document.getElementById('fileInput');
const btnUpload = document.getElementById('btnUpload');
const imgPreviewContainer = document.getElementById('imgPreviewContainer');
const imgPreview = document.getElementById('imgPreview');
const removeImgBtn = document.getElementById('removeImgBtn');
let currentImageData = null;
"""
full_content = full_content.replace(js_vars_anchor, new_js_vars)

# Add file input listener
js_event_anchor = "/* backend caller */"
new_js_logic = """
/* Image upload handling */
btnUpload.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = (event) => {
    currentImageData = event.target.result.split(',')[1]; // Get base64 part
    imgPreview.src = event.target.result;
    imgPreviewContainer.style.display = 'block';
  };
  reader.readAsDataURL(file);
});

removeImgBtn.addEventListener('click', () => {
  currentImageData = null;
  imgPreview.src = '';
  imgPreviewContainer.style.display = 'none';
  fileInput.value = '';
});

/* backend caller */
"""
full_content = full_content.replace(js_event_anchor, new_js_logic)

# Update callChatAPI parameters and payload
api_call_anchor = "async function callChatAPI(message, deviceId='device-0'){"
new_api_call = "async function callChatAPI(message, deviceId='device-0', imageData=null){"
full_content = full_content.replace(api_call_anchor, new_api_call)

payload_anchor = "const payload = { user_id: 'indira', message: message, device_id: deviceId };"
new_payload = "const payload = { user_id: 'indira', message: message, device_id: deviceId, image_data: imageData || currentImageData };"
full_content = full_content.replace(payload_anchor, new_payload)

# Inside callChatAPI, clear image data and preview on success
append_msg_anchor = "appendMessage('user', message, {time: new Date().toLocaleTimeString()});"
new_append_msg = """appendMessage('user', message, {time: new Date().toLocaleTimeString()});
  if(currentImageData) {
    const lastMsgRow = chatArea.lastElementChild;
    const bubble = lastMsgRow.querySelector('.bubble');
    const img = document.createElement('img');
    img.src = 'data:image/jpeg;base64,' + currentImageData;
    bubble.appendChild(img);
  }
"""
full_content = full_content.replace(append_msg_anchor, new_append_msg)

clear_img_anchor = "speak(j.response);"
new_clear_img = """speak(j.response);
      // Clear image
      currentImageData = null;
      imgPreviewContainer.style.display = 'none';
      fileInput.value = '';
"""
full_content = full_content.replace(clear_img_anchor, new_clear_img)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(full_content)

print("UI Patch successful")
