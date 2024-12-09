import axios from 'axios';
import storeData from './storeData';

export async function getStats(token, refresh_tok) {
  try {
    const kits = await axios.get('http://62.109.17.249:8006/users/me/kits', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    storeData("kits_count", JSON.stringify(kits.data.length));

    const researches = await axios.get('http://62.109.17.249:8006/users/me/researches', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
  
      storeData("researches_count", JSON.stringify(researches.data.length));

      const scans = await axios.get('http://62.109.17.249:8006/users/me/samples', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
  
      storeData("scans_count", JSON.stringify(scans.data.length));

  } catch (error) {
    console.log(error);
    if (error.response.status == 401) {
        console.log("Refreshing token...");
        const response = await axios.get('http://62.109.17.249:1337/refresh', new URLSearchParams({refresh_token: refresh_tok}), {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
      
        storeData("refresh_token", response.data.refresh_token);
        getStats(token);
    }
    console.error('Error logging in:', error);

    throw error; // Rethrow the error for the caller to handle
  }
}

