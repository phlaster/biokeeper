import AsyncStorage from '@react-native-async-storage/async-storage';

export default async function storeData (key, value) {
    try {
      await AsyncStorage.setItem(key, value);
    } catch (error) {
      console.error("Error on saving data to local storage", error);
      Alert.alert('Error', `Error on saving data to local storage.\n${error}`, [{ text: 'OK' }]);
    }
  };