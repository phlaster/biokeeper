import React, { useState, useEffect } from "react";
import { Dimensions, Alert, Vibration, Pressable, View } from "react-native";
import { Button, Text, Surface } from 'react-native-paper';
import { Camera, CameraView } from 'expo-camera';
import { router } from "expo-router";
import * as Linking from "expo-linking";
import styles from '../styles/style';

function QRScanner({ navigation }) {
  const [hasPermissions, setHasPermissions] = useState(false);
  const [isCameraFrozen, setIsCameraFrozen] = useState(false);
  const [scannedData, setScannedData] = useState(null);

  useEffect(() => {
    (async () => {
      const { status: cameraStatus } = await Camera.requestCameraPermissionsAsync();
      setHasPermissions(cameraStatus === "granted" );
    })();
  }, []);

  
  // useEffect(() => {
  //   if (hasPermissions === false) {
  //     Alert.alert(
  //       "Camera Permissions Required",
  //       "You must grant access to your camera to scan QR codes",
  //       [
  //         { text: "Go to settings", onPress: () => Linking.openSettings() },
  //         { text: "Cancel", onPress: () => router.dismissAll(), style: "cancel" },
  //       ]
  //     );
  //   }
  // }, [hasPermissions]);

  const handleBarCodeScanned = ({ data }) => {
    Vibration.vibrate([0, 70]);
    setScannedData(data);
    setIsCameraFrozen(true);
  };

  const handleScanAgain = () => {
    setScannedData(null);
    setIsCameraFrozen(false);
  };

  const handleProceed = () => {
    navigation.navigate('After_Scan', { data: scannedData });
  };

  if (!hasPermissions) {
    return null;
  }

  return (
<View style={styles.cameraContainer}>
      {isCameraFrozen && (
        <View style={styles.qrContentBox}>
          <Text style={styles.qrContentText}>{scannedData}</Text>
        </View>
      )}
      <CameraView
        onBarcodeScanned={isCameraFrozen ? undefined : handleBarCodeScanned}
        barcodeScannerSettings={{ barcodeTypes: ["qr"] }}
        style={styles.cameraView}
      />
      <View style={styles.buttonContainer}>
        <Button style={[styles.buttonCamera, styles.cancelButton]} onPress={() => navigation.navigate('LK')}>
          <Text style={styles.buttonText}>Cancel</Text>
        </Button>
        <Button 
          style={[styles.buttonCamera, isCameraFrozen ? {} : styles.disabledButton]} 
          onPress={handleScanAgain} 
          disabled={!isCameraFrozen}
        >
          <Text style={styles.buttonText}>Scan again</Text>
        </Button>
        <Button 
          style={[styles.buttonCamera, isCameraFrozen ? {} : styles.disabledButton]} 
          onPress={handleProceed} 
          disabled={!isCameraFrozen}
        >
          <Text style={styles.buttonText}>Proceed</Text>
        </Button>
      </View>
    </View>
  );
}
export default QRScanner;