import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const sendChatMessage = async (message, scope = 'auto') => {
  try {
    const response = await axios.post(`${API_URL}/chat`, {
      message: message,
      scope: scope
    });
    return response.data;
  } catch (error) {
    console.error("Lỗi gọi API:", error);
    return null;
  }
};

export const sendFeedback = async (messageId, type, note = "", question = "", answer = "") => {
  try {
    await axios.post(`${API_URL}/feedback`, {
      message_id: messageId,
      feedback_type: type,
      user_note: note,
      question: question, // Gửi xuống BE
      answer: answer      // Gửi xuống BE
    });
  } catch (error) {
    console.error("Lỗi gửi feedback:", error);
  }
};