export default function Request(method, url, data) {
    var request = new XMLHttpRequest();



    request.onreadystatechange = (e) => {
      if (request.readyState !== 4) {
        return;
      }
      if (request.status === 200) {
        console.log('success:' + request.responseText);
      } else {
        console.log('error:' + request.status);
      }
    };
    
    request.open(method, url + "?" + new URLSearchParams(data).toString());
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify(data));
}