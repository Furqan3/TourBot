import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

export const sendChatQuery = async (query) => {
  try {
    const response = await axios.post(`${API_URL}/chat`, {
      query: query
    });
    return response.data;
  } catch (error) {
    console.error('Error sending chat query:', error);
    throw error;
  }
};