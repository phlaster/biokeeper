import AsyncStorage from '@react-native-async-storage/async-storage';

export default async function storeData (key, value) {
    try {
      await AsyncStorage.setItem(key, value);
    } catch (e) {
      console.error("Ошибка при сохранении данных", e);
    }
  };