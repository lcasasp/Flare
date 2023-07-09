import axios from 'axios';

const baseURL = 'http://127.0.0.1:5000'; 

export const fetchData = async () => {
    try {
      const response = await axios.get(`${baseURL}/news`); // Replace "/api/data" with your backend API route
      return response.data;
    } catch (error) {
      console.error('Error fetching data:', error);
      throw error;
    }
};

export const searchArticles = async (searchQuery: string) => {
    try {
        const response = await axios.post(`${baseURL}/query`, { search_query: searchQuery }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error searching articles:', error);
        throw error;
    }
};