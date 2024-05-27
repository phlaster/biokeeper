import AsyncStorage from '@react-native-async-storage/async-storage';


export default async function getData (key) {
  try {
    const value = await AsyncStorage.getItem(key);
    if(value !== null) {
      // значение найдено
      return value;
    }
  } catch(e) {
    // ошибка при чтении данных
    console.error("Ошибка при чтении данных", e);
  }
};