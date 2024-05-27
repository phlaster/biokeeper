import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Request from './Requests';
import { RadioButtons } from 'react-native-radio-buttons'


const getData = async (key) => {
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

export default function LK({navigation}) {

  const loadscene=()=>{
    navigation.navigate('Qr_screen');
  }

  const exit = async()  => {
    let username='username',
        password='password';

    try {
      await AsyncStorage.removeItem(username);
      await AsyncStorage.removeItem(password);
      navigation.navigate('Autorization');
    } catch(e) {
      // ошибка при удалении данных
      console.error("Ошибка при удалении данных", e);
    }

  };

  function renderOption(option, selected, onSelect, index){
    const style = selected ? { fontWeight: 'bold'} : {};
 
    return (
      <TouchableWithoutFeedback onPress={onSelect} key={index}>
        <Text style={style}>{option}</Text>
      </TouchableWithoutFeedback>
    );
  }



  const [Options, setOptions] = useState('');
  const [SelectedOption, setSelectedOption] = useState('');

    useEffect(() => {
      const fetchData = async () => {
        const login = await getData('username');
        const password = await getData('password');
        if (login && password) {
          const researches = Request('POST', 'http://62.109.17.249:8000/react/researches', {username: login, password: password}).then(data => {
          console.log(data);  
          if (!data.result) {
              Alert.alert("Ошибка:\n" + data.response);
            }
            
            setOptions(Array.from(Object.values(data.response), r=>r.name));
            console.log(Options);

          })
          .catch(error => {
            console.error('Error:', error);
          });
        }
        else {
          Alert.alert("Invalid Login or Password");
        }
      };

      fetchData();
    }, []);


  return (
    
    <View style={styles.container}>
          <View style={{margin: 20}}>
                <RadioButtons
                  options={ Options }
                  onSelection={ setSelectedOption }
                  selectedOption={ SelectedOption }
                  renderOption={ renderOption }
                  renderContainer={ (optionNodes)=> {<View>{optionNodes}</View>} }
                />
                <Text>Selected option: { SelectedOption || 'none'}</Text>
          </View>
              
      <Button style={styles.btn} title={'сканировать QR'} onPress={loadscene}/>

      <Button style={styles.btn} title={'выйти'} onPress={exit}/>
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
    //backgroundColor: 'purple',
  },
  text: {
    color:'green', 
    marginBottom: 10
  },
  textLast:
  {
    color:'green', 
    marginTop: 50,
    marginBottom: 10
  },
  btn:{
    position:'relative',
    bottom:0
  }
});
