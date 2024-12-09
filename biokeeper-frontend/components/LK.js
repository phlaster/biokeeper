import { useFocusEffect } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, BackHandler, Alert } from 'react-native';
import { Text, Button, Surface, Avatar } from 'react-native-paper';


import styles from '../styles/style';
import getData from './getData';
import { auth } from './Authfunc';
import { getStats } from './Utils';

export default function LK({ navigation }) {
  const [userData, setUserData] = useState({ name: '', email: 'some@email.com' });
  const [stats, setStats] = useState({ totalScans: 0, researches: 0, kits: 0 });
  const [isOffline, setIsOffline] = useState(false);

  useFocusEffect(
    useCallback(() => {
      navigation.setOptions({
        headerLeft: null,
        gestureEnabled: false,
      });
    }, [navigation])
  );

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    const backHandler = BackHandler.addEventListener("hardwareBackPress", () => true);
    return () => backHandler.remove();
  }, []);

  const fetchData = async () => {
    const offlineMode = await getData('offline_mode');
    const username = await getData('current_user');

    await getStats(await getData('access_token'), await getData('refrash_token'));

    const scansCount = await getData('scans_count');
    const researchesCount = await getData('researches_count');
    const kitsCount = await getData('kits_count');

    setUserData({ ...userData, name: username });
    setStats({ totalScans: scansCount, researches: researchesCount, kits: kitsCount });
    if (offlineMode === '1') {
      setIsOffline(true);
    } else {
      const access_token = await getData('access_token');
      if (!access_token) {
        navigation.replace('Authorization');
      }
    }
  };

  const handleLogout = async () => {
    if (isOffline) {
      try {
        const username = await getData('current_user');
        const password = await getData('current_password');
        const authStatus = await auth({
          grant_type: 'password',
          username: username,
          password: password,
        });
        if (authStatus === 401) {
          await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'offline_mode']);
          navigation.replace('Authorization');
        } else {
          await AsyncStorage.setItem('offline_mode', '0');
          setIsOffline(false);
        }
      } catch (error) {
        console.error('Network error:', error);
        Alert.alert('Couldn\'t connect to server', 'Please check your internet connection and try again.', [{ text: 'OK' }]);
      }
    } else {
      try {
        await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'offline_mode']);
        navigation.replace('Authorization');
      } catch (error) {
        console.error("Error removing data upon logout", error);
        Alert.alert('Error', `Error removing data upon logout.\n${error}`, [{ text: 'OK' }]);
      }
    }
  };

  const navigateTo = (screen) => {
    navigation.navigate(screen);
  };

  const getButtonStyles = (label) => {
    return {
      containerStyle: label === 'Connect' ? styles.connectButton : styles.logoutButton,
      labelStyle: label === 'Connect' ? styles.connectButtonLabel : styles.logoutButtonLabel,
    };
  };

  
  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      <View style={styles.container}>
        <View style={styles.statusBar}>
          <Avatar.Image size={80} source={require('../assets/LK.png')} />
          <View style={styles.statusBarUserInfo}>
            <Text style={styles.statusBarUsername}>{userData.name}</Text>
            <Text style={styles.statusBarEmail}>{userData.email}</Text>
          </View>
          <Button
            style={[styles.statusBarLogoutButton, getButtonStyles(isOffline ? 'Connect' : 'Log Out').containerStyle]}
            labelStyle={[styles.statusBarLogoutButtonLabel, getButtonStyles(isOffline ? 'Connect' : 'Log Out').labelStyle]}
            mode="outlined"
            onPress={handleLogout}
          >
            {isOffline ? 'Connect' : 'Log Out'}
          </Button>
        </View>

        <View style={styles.buttonGrid}>
          <Button mode="contained" onPress={() => navigateTo('Qr_screen')} style={styles.gridButton}>
            Scan
          </Button>
          <Button mode="contained" onPress={() => navigateTo('MyScans')} style={styles.gridButton}>
            My Scans
          </Button>
          <Button mode="contained" onPress={() => { }} style={styles.gridButton}>
            Activate KIT
          </Button>
          <Button mode="contained" onPress={() => { }} style={styles.gridButton}>
            My Kits
          </Button>
        </View>

        <Surface style={styles.statsSurface}>
          <Text style={styles.statsTitle}>Statistics</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats.totalScans}</Text>
              <Text style={styles.statLabel}>Total scans</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats.researches}</Text>
              <Text style={styles.statLabel}>Researches</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats.kits}</Text>
              <Text style={styles.statLabel}>Kits</Text>
            </View>
          </View>
        </Surface>
      </View>
    </ScrollView>
  );
}