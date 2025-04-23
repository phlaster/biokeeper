import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, FlatList, Dimensions, TouchableOpacity, Modal, Button } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import getData from './getData';

const { width } = Dimensions.get('window');

export default function MyScans({ navigation }) {
  const [scans, setScans] = useState([]);
  const [selectedScan, setSelectedScan] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    const fetchScans = async () => {
      try {
        const username = await getData('current_user');
        const keys = await AsyncStorage.getAllKeys();
        const scanKeys = keys.filter(key => key.startsWith(`scan_${username}_`));
        const scanData = await AsyncStorage.multiGet(scanKeys);
        const parsedScans = scanData.map(([key, value], index) => {
          const scan = JSON.parse(value);
          return {
            id: scan.id,
            time: new Date(parseInt(scan.id)).toLocaleString(),
            comment: scan.comment ? scan.comment.slice(0, 15) + (scan.comment.length > 15 ? '...' : '') : '',
            sendStatus: 'Not Sent',
          };
        });
        setScans(parsedScans);
      } catch (error) {
        console.error('Error fetching scans:', error);
        Alert.alert('Error', `Error fetching scans.\n${error}`, [{ text: 'OK' }]);
      }
    };

    fetchScans();
  }, []);

  const renderItem = ({ item, index }) => (
    <TouchableOpacity onPress={() => { setSelectedScan(item); setModalVisible(true); }}>
      <View style={styles.row}>
        <Text style={[styles.cell, styles.indexCell]}>{index + 1}</Text>
        <Text style={[styles.cell, styles.timeCell]}>{item.time}</Text>
        <Text style={[styles.cell, styles.commentCell]}>{item.comment}</Text>
        <Text style={[styles.cell, styles.statusCell]}>{item.sendStatus}</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={scans}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        ListHeaderComponent={() => (
          <View style={styles.header}>
            <Text style={[styles.headerCell, styles.indexCell]}>No</Text>
            <Text style={[styles.headerCell, styles.timeCell]}>Time</Text>
            <Text style={[styles.headerCell, styles.commentCell]}>Comment</Text>
            <Text style={[styles.headerCell, styles.statusCell]}>Status</Text>
          </View>
        )}
      />
      <TouchableOpacity style={styles.homeButton} onPress={() => navigation.navigate('LK')}>
        <Text style={styles.homeButtonText}>Home</Text>
      </TouchableOpacity>
      <StatusBar style="auto" />

      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => { setModalVisible(!modalVisible); }}
      >
        <View style={styles.centeredView}>
          <View style={styles.modalView}>
            <Text style={styles.modalText}>ID: {selectedScan?.id}</Text>
            <Text style={styles.modalText}>Time: {selectedScan?.time}</Text>
            <Text style={styles.modalText}>Comment: {selectedScan?.comment}</Text>
            <Text style={styles.modalText}>Status: {selectedScan?.sendStatus}</Text>
            <View style={styles.modalButtonContainer}>
              <Button title="Close" onPress={() => setModalVisible(!modalVisible)} />
              <Button title="Send" onPress={() => {}} />
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    backgroundColor: '#f0f0f0',
    borderBottomWidth: 1,
    borderBottomColor: '#ccc',
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  headerCell: {
    fontWeight: 'bold',
    fontSize: 16,
    textAlign: 'left',
    color: '#333',
  },
  row: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  cell: {
    fontSize: 14,
    color: '#444',
  },
  indexCell: {
    width: width * 0.1,
    textAlign: 'center',
  },
  timeCell: {
    width: width * 0.35,
  },
  commentCell: {
    width: width * 0.35,
  },
  statusCell: {
    width: width * 0.2,
    textAlign: 'center',
  },
  homeButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 15,
    alignItems: 'center',
    borderRadius: 5,
    margin: 10,
  },
  homeButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  centeredView: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 22,
  },
  modalView: {
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 35,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  modalText: {
    marginBottom: 15,
    textAlign: 'center',
  },
  modalButtonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
});