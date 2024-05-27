import React from 'react';
import { Text, StyleSheet, View, Button } from 'react-native';


export default function MarkdownScreen({route, navigation}) {
  const { data } = route.params;
  console.log("Data(comment) in the next page:" + data);
  const markdownText = data;
  console.log(markdownText);

  return (
    <View>
        <Text>
            {markdownText}
        </Text>

        <Button style={styles.btn} title={'Дальше'} onPress={()=>{navigation.navigate('Qr_screen');}} />
        <Button style={styles.btn} title={'Назад'} onPress={()=>{navigation.navigate('LK');}} />
    </View>
    

  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    backgroundColor: '#fff',
  },
});