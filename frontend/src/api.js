import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const sendChatMessage = async (message, scope = 'auto', isFirstMessage = true, sessionId = null, apiKey = '') => {
  try {
    const payload = { message, scope, is_first_message: isFirstMessage };
    if (sessionId) payload.session_id = sessionId;
    const headers = {};
    if (apiKey) headers['X-API-Key'] = apiKey;
    const response = await axios.post(`${API_URL}/chat`, payload, { headers });
    return response.data;
  } catch (error) {
    console.error('Lỗi gọi API:', error);
    return null;
  }
};

/**
 * Streaming chat — đọc SSE từ /chat/stream
 * Callbacks: onThinking(stage, message), onToken(text), onDone(data), onError(msg)
 */
export const sendChatMessageStream = async (
  message,
  scope = 'auto',
  isFirstMessage = true,
  sessionId = null,
  apiKey = '',
  { onThinking, onToken, onDone, onError } = {}
) => {
  const payload = { message, scope, is_first_message: isFirstMessage };
  if (sessionId) payload.session_id = sessionId;

  const headers = { 'Content-Type': 'application/json' };
  if (apiKey) headers['X-API-Key'] = apiKey;

  try {
    const response = await fetch(`${API_URL}/chat/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      onError?.(`Lỗi kết nối (HTTP ${response.status})`);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? ''; // giữ lại dòng chưa hoàn chỉnh

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === 'thinking') onThinking?.(data.stage, data.message);
          else if (data.type === 'token')   onToken?.(data.text);
          else if (data.type === 'done')    onDone?.(data);
          else if (data.type === 'error')   onError?.(data.message);
        } catch {
          // bỏ qua dòng JSON không hợp lệ
        }
      }
    }
  } catch (error) {
    console.error('Lỗi stream API:', error);
    onError?.(error.message || 'Lỗi kết nối');
  }
};

export const sendFeedback = async (messageId, type, note = '', question = '', answer = '') => {
  try {
    await axios.post(`${API_URL}/feedback`, {
      message_id: messageId,
      feedback_type: type,
      user_note: note,
      question,
      answer,
    });
  } catch (error) {
    console.error('Lỗi gửi feedback:', error);
  }
};

export const clearSession = async (sessionId) => {
  try {
    await axios.delete(`${API_URL}/session/${sessionId}`);
  } catch (error) {
    console.error('Lỗi xoá session:', error);
  }
};
