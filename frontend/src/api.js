import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const sendChatMessage = async (message, scope = 'auto', isFirstMessage = true, sessionId = null) => {
  try {
    const payload = { message, scope, is_first_message: isFirstMessage };
    if (sessionId) payload.session_id = sessionId;
    const response = await axios.post(`${API_URL}/chat`, payload);
    return response.data;
  } catch (error) {
    console.error('Lỗi gọi API:', error);
    return null;
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
