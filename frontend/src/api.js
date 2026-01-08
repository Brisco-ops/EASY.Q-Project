const API_BASE = '';

// Generate or get session ID for conversation memory
function getSessionId() {
  let sessionId = localStorage.getItem('chat_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
    localStorage.setItem('chat_session_id', sessionId);
  }
  return sessionId;
}

export const api = {
  getSessionId,
  
  async getMenu(slug, lang = 'en') {
    const res = await fetch(`${API_BASE}/api/public/menus/${slug}?lang=${lang}`);
    if (!res.ok) throw new Error('Menu not found');
    return res.json();
  },
  
  async getConversation(slug) {
    const sessionId = getSessionId();
    const res = await fetch(`${API_BASE}/api/public/menus/${slug}/conversation?session_id=${sessionId}`);
    if (!res.ok) return { messages: [] };
    return res.json();
  },
  
  async clearConversation(slug) {
    const sessionId = getSessionId();
    await fetch(`${API_BASE}/api/public/menus/${slug}/conversation?session_id=${sessionId}`, {
      method: 'DELETE'
    });
  },

  async chat(slug, messages, lang = 'en') {
    const sessionId = getSessionId();
    const res = await fetch(`${API_BASE}/api/public/menus/${slug}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, lang, session_id: sessionId }),
    });
    if (!res.ok) throw new Error('Chat error');
    return res.json();
  },

  async *chatStream(slug, messages, lang = 'en') {
    const sessionId = getSessionId();
    const res = await fetch(`${API_BASE}/api/public/menus/${slug}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, lang, session_id: sessionId }),
    });
    
    if (!res.ok) throw new Error('Chat error');
    
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') return;
          if (data.startsWith('[ERROR]')) throw new Error(data);
          yield data;
        }
      }
    }
  },

  async uploadMenu(restaurantName, pdfFile, languages = 'en,fr,es') {
    const formData = new FormData();
    formData.append('restaurant_name', restaurantName);
    formData.append('languages', languages);
    formData.append('pdf', pdfFile);
    
    const res = await fetch(`${API_BASE}/api/menus`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Upload failed');
    }
    return res.json();
  },
};
