import axios from 'axios';
import storeData from './storeData';

export async function auth(params) {
  try {
    const response = await axios.post('http://62.109.17.249:1337/token', new URLSearchParams(params), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    storeData("access_token", response.data.access_token);
    storeData("refresh_token", response.data.refresh_token);
    return response.status; // Return the status for further handling

  } catch (error) {
    console.error('Error logging in:', error);

    throw error; // Rethrow the error for the caller to handle
  }
}

export async function reg(params) {
  try {
    const response = await axios.post('http://62.109.17.249:1337/create', params, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    storeData("authStatus", error.response ? error.response.status : 500);
    console.error('Error registering:', error);
    throw error; // Rethrow the error for the caller to handle
  }
}