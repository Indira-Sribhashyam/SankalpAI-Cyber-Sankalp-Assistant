# SankalpAI Chatbot Integration Guide

This guide explains how to integrate the SankalpAI Chatbot into your existing dashboard as a floating widget.

## 1. Prerequisites
- The Assistant API must be running (e.g., on `http://localhost:8000`).
- Your dashboard must allow embedding `iframe` elements.

## 2. Integration Code

Copy and paste the following HTML/CSS snippet into your dashboard's main HTML file (e.g., `index.html`), preferably just before the closing `</body>` tag.

```html
<!-- SankalpAI Floating Widget -->
<div id="sankalp-widget-container" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end;">
    
    <!-- Chat Frame (Hidden by default) -->
    <div id="sankalp-chat-frame" style="display: none; width: 400px; height: 600px; margin-bottom: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); border-radius: 12px; overflow: hidden; border: 1px solid rgba(100, 255, 218, 0.3);">
        <iframe src="http://localhost:8000/chat-ui?mode=widget" style="width: 100%; height: 100%; border: none; background: #0a192f;"></iframe>
    </div>

    <!-- Floating Toggle Button -->
    <button onclick="toggleSankalpChat()" style="width: 60px; height: 60px; border-radius: 50%; background: #0a192f; border: 2px solid #64ffda; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(100, 255, 218, 0.4); transition: transform 0.2s;">
        <!-- Icon (Simple SVG) -->
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#64ffda" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
    </button>
</div>

<script>
    function toggleSankalpChat() {
        const frame = document.getElementById('sankalp-chat-frame');
        if (frame.style.display === 'none') {
            frame.style.display = 'block';
        } else {
            frame.style.display = 'none';
        }
    }
</script>
```

## 3. Customization

- **Position**: Change `bottom: 20px; right: 20px;` to move the button.
- **Size**: Change `width: 400px; height: 600px;` to resize the chat window.
- **URL**: If you deploy the assistant to a server, change `http://localhost:8000` to your actual server URL.

## 4. Testing
1. Open your dashboard in a browser.
2. Click the floating chat icon in the bottom-right corner.
3. The SankalpAI assistant should open in a clean, compact "Widget Mode".
