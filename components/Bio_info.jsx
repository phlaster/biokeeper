import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, Alert, View, Button, TextInput } from 'react-native';
import * as Location from 'expo-location';
import storeData from './storeData';
import getData from './getData';


const Request = async (method, url, data) => {
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


const getLocationPermission = async () => {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') {
    console.log('Permission to access location was denied');
    return false;
  }
  return true;
};


export default function Bio_info({ route, navigation }) {
  const [location, setLocation] = useState(null);
  const [storedGeoData, setStoredGeoData] = useState('');
  const handleSave = () => {
    
    storeData('GeoData', JSON.stringify(location));
    
  };
  useEffect(() => {
    const getLocation = async () => {
      const permissionGranted = await getLocationPermission();
      if (permissionGranted) {
        const currentLocation = await Location.getCurrentPositionAsync({});
        setLocation(currentLocation.coords);
      }
    };

    getLocation();
  }, []); // Run only once on component mount

  

  const { data } = route.params;
  const loadscene = () => {
    // Define the functionality for loadscene
    Alert.alert(
      "Теперь можно сфотографировать местность"
    );
    
    navigation.navigate('Take_photo');
  };

  const sendData = async () => {
    const src = await Request('POST', 'http://62.109.17.249:8000/react/push_sample', {
      username: inputLogin,
      password: inputPassword,
      qr_unique_hex: data,
      research_name: getData("research"),
      collected_at: (new Date()).toISOString(),
      latitude: location.latitude,
      longitude: location.latitude
    });
    console.log(src);

    if (src.result) {
      //await storeData("src", JSON.stringify(src));
      Alert.alert(src.response);
    } else {
      Alert.alert(src.response);
    }
  };

  const [inputValue, setInputValue] = useState(''); 
  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        onChangeText={setInputValue} 
        value={inputValue}
        placeholder="Введите комментарий"
      />
      <Text>Latitude: {location ? location.latitude : 'Loading...'}</Text>
      <Text>Longitude: {location ? location.longitude : 'Loading...'}</Text>
      <Text>Comment: {inputValue ? inputValue : 'Loading...'}</Text>
      <Text>qr: {data}</Text>
      <Button title={'Фото'} onPress={loadscene} />
      
      <Button title="Сохранить данные" onPress={handleSave} />
      <Button title="Отправить данные" onPress={sendData} />
      
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    color: 'green',
    marginBottom: 20,
  },
  logo: {
    width: 250,
    height: 250,
  },
  input: {
    height: 40,
    width: '80%',
    borderColor: 'gray',
    borderWidth: 1,
    padding: 10,
    marginBottom: 20,
  },
});
