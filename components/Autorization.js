import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button} from 'react-native';


export default function Autorization({navigation}) {
const loadscene=()=>{
  navigation.navigate('Qr_screen');
}

  return (
    <View style={styles.container}>
      
      
      
      <Text style={styles.text}>Авторизируйся</Text>
       <Button style={styles.btn} title={'Продолжить'} onPress={loadscene}/>

       <Text style={styles.textLast}>Продолжить без авторизации</Text>
       <Button style={styles.btn} title={'Продолжить'} onPress={loadscene}/>
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
  
});
