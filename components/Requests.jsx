export default async function Request(method, url, data) {
  try {
    const response = await fetch(url + "?" + new URLSearchParams(data).toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    const resp = await response.json();
    
    return resp;
  } catch (error) {
    console.error('There has been a problem with your fetch operation:', error);
    throw error;
  }
}