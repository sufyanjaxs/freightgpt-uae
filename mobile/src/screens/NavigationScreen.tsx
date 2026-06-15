import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Geolocation from '@react-native-community/geolocation';
import { trackingApi } from '../services/api';

export default function NavigationScreen({ route, navigation }: any) {
  const { tripId } = route.params;
  const [location, setLocation] = useState({ lat: 25.2048, lng: 55.2708 });
  const [eta, setEta] = useState('---');
  const [voiceMode, setVoiceMode] = useState(false);

  useEffect(() => {
    const watchId = Geolocation.watchPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setLocation({ lat: latitude, lng: longitude });
        trackingApi.updateLocation(tripId, latitude, longitude).catch(() => {});
      },
      (err) => console.error(err),
      { enableHighAccuracy: true, distanceFilter: 100, interval: 30000 },
    );

    return () => Geolocation.clearWatch(watchId);
  }, [tripId]);

  return (
    <View style={styles.container}>
      <View style={styles.mapPlaceholder}>
        <Text style={styles.mapIcon}>🗺️</Text>
        <Text style={styles.mapText}>Live Navigation</Text>
        <Text style={styles.coords}>
          {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
        </Text>
      </View>

      <View style={styles.infoCard}>
        <View style={styles.infoRow}>
          <View>
            <Text style={styles.infoLabel}>Next Turn</Text>
            <Text style={styles.infoValue}>Continue straight for 2.5 km</Text>
          </View>
        </View>
        <View style={styles.infoRow}>
          <View>
            <Text style={styles.infoLabel}>ETA</Text>
            <Text style={styles.infoValue}>{eta}</Text>
          </View>
          <View>
            <Text style={styles.infoLabel}>Distance Remaining</Text>
            <Text style={styles.infoValue}>156 km</Text>
          </View>
        </View>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.actionButton, voiceMode && styles.actionButtonActive]}
          onPress={() => setVoiceMode(!voiceMode)}>
          <Text style={styles.actionButtonText}>
            {voiceMode ? '🎙️ Voice Active' : '🎤 Voice Mode'}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('DocumentUpload', { tripId })}>
          <Text style={styles.actionButtonText}>📄 Upload POD</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.quickInfo}>
        <View style={styles.quickItem}>
          <Text style={styles.quickValue}>45 L</Text>
          <Text style={styles.quickLabel}>Fuel Level</Text>
        </View>
        <View style={styles.quickItem}>
          <Text style={styles.quickValue}>82 km/h</Text>
          <Text style={styles.quickLabel}>Speed</Text>
        </View>
        <View style={styles.quickItem}>
          <Text style={styles.quickValue}>3.5h</Text>
          <Text style={styles.quickLabel}>Driving Time</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a', padding: 16 },
  mapPlaceholder: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    height: 250,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  mapIcon: { fontSize: 48 },
  mapText: { color: '#fff', fontSize: 18, fontWeight: '600', marginTop: 8 },
  coords: { color: '#64748b', fontSize: 14, marginTop: 4 },
  infoCard: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8 },
  infoLabel: { color: '#64748b', fontSize: 12 },
  infoValue: { color: '#fff', fontSize: 16, fontWeight: '500' },
  actions: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  actionButton: {
    flex: 1,
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#334155',
  },
  actionButtonActive: { borderColor: '#22c55e', backgroundColor: '#1a3a2a' },
  actionButtonText: { color: '#fff', fontSize: 14, fontWeight: '500' },
  quickInfo: { flexDirection: 'row', justifyContent: 'space-around', backgroundColor: '#1e293b', borderRadius: 16, padding: 16 },
  quickItem: { alignItems: 'center' },
  quickValue: { color: '#60a5fa', fontSize: 20, fontWeight: 'bold' },
  quickLabel: { color: '#64748b', fontSize: 12, marginTop: 4 },
});
