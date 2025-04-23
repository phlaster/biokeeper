import React from 'react';
import { ScrollView, StyleSheet, View, Button } from 'react-native';
import Markdown from 'react-native-markdown-display';

export default function MarkdownScreen({ route, navigation }) {
  const { data } = route.params;
  console.log("Data(comment) in the next page:" + data);
  const markdownText = data;
  console.log(markdownText);

  return (
    <View style={styles.container}>
      <ScrollView>
        <Markdown>
          {markdownText}
        </Markdown>
      </ScrollView>

      <View style={styles.buttonContainer}>
        <Button title={'Назад'} onPress={() => { navigation.navigate('LK'); }} />
        <Button title={'Дальше'} onPress={() => { navigation.navigate('Qr_screen'); }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    backgroundColor: '#fff',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
});