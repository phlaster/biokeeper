import AsyncStorage from '@react-native-async-storage/async-storage';


export default async function getData (key) {
  try {
    const value = await AsyncStorage.getItem(key);
    if(value !== null) {
      return value;
    }
  } catch(error) {
    console.error("Error reading data from local storage", error);
    Alert.alert('Error', `Error reading data from local storage.\n${error}`, [{ text: 'OK' }]);
  }
};