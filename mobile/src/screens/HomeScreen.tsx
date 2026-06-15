import React, { useEffect, useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  RefreshControl, ActivityIndicator
} from 'react-native';
import { tripsApi } from '../services/api';

export default function HomeScreen({ navigation }: any) {
  const [currentTrip, setCurrentTrip] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadTrips = async () => {
    try {
      const { data } = await tripsApi.current();
      if (data?.items?.length > 0) {
        setCurrentTrip(data.items[0]);
      }
    } catch (err) {
      console.error('Failed to load trips:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadTrips();
  }, []);

  const quickActions = [
    { title: 'Navigate', icon: '🗺️', screen: 'Navigation', color: '#2563eb' },
    { title: 'Upload POD', icon: '📄', screen: 'DocumentUpload', color: '#16a34a' },
    { title: 'My Profile', icon: '👤', screen: 'Profile', color: '#9333ea' },
    { title: 'Support', icon: '🎧', screen: 'Profile', color: '#ea580c' },
  ];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadTrips(); }} />
      }>
      {currentTrip ? (
        <View style={styles.activeTrip}>
          <View style={styles.tripHeader}>
            <Text style={styles.tripTitle}>Active Trip</Text>
            <View style={styles.tripStatus}>
              <View style={styles.statusDot} />
              <Text style={styles.statusText}>In Transit</Text>
            </View>
          </View>
          <Text style={styles.route}>
            {currentTrip.origin_city} → {currentTrip.destination_city}
          </Text>
          <View style={styles.tripDetails}>
            <View>
              <Text style={styles.detailLabel}>Pickup</Text>
              <Text style={styles.detailValue}>
                {new Date(currentTrip.pickup_date).toLocaleDateString()}
              </Text>
            </View>
            {currentTrip.distance_km && (
              <View>
                <Text style={styles.detailLabel}>Distance</Text>
                <Text style={styles.detailValue}>{currentTrip.distance_km} km</Text>
              </View>
            )}
          </View>
          <TouchableOpacity
            style={styles.navigateButton}
            onPress={() => navigation.navigate('Navigation', { tripId: currentTrip.id })}>
            <Text style={styles.navigateButtonText}>Start Navigation</Text>
          </TouchableOpacity>
        </View>
      ) : !loading ? (
        <View style={styles.noTrip}>
          <Text style={styles.noTripIcon}>🛣️</Text>
          <Text style={styles.noTripText}>No active trips</Text>
          <Text style={styles.noTripSubtext}>You'll see your assigned trips here</Text>
        </View>
      ) : null}

      <Text style={styles.sectionTitle}>Quick Actions</Text>
      <View style={styles.actionsGrid}>
        {quickActions.map((action, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.actionCard, { borderColor: action.color }]}
            onPress={() => navigation.navigate(action.screen)}>
            <Text style={styles.actionIcon}>{action.icon}</Text>
            <Text style={styles.actionTitle}>{action.title}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a', padding: 16 },
  activeTrip: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#334155',
  },
  tripHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  tripTitle: { fontSize: 18, fontWeight: 'bold', color: '#fff' },
  tripStatus: { flexDirection: 'row', alignItems: 'center' },
  statusDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#22c55e', marginRight: 6 },
  statusText: { color: '#22c55e', fontSize: 14 },
  route: { fontSize: 20, fontWeight: '600', color: '#60a5fa', marginBottom: 16 },
  tripDetails: { flexDirection: 'row', gap: 32, marginBottom: 16 },
  detailLabel: { color: '#64748b', fontSize: 12, marginBottom: 4 },
  detailValue: { color: '#fff', fontSize: 16, fontWeight: '500' },
  navigateButton: { backgroundColor: '#2563eb', borderRadius: 12, padding: 14, alignItems: 'center' },
  navigateButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  noTrip: { alignItems: 'center', paddingVertical: 48, marginBottom: 24 },
  noTripIcon: { fontSize: 48, marginBottom: 12 },
  noTripText: { fontSize: 20, fontWeight: 'bold', color: '#fff' },
  noTripSubtext: { color: '#64748b', marginTop: 4 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#fff', marginBottom: 16 },
  actionsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  actionCard: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 20,
    width: '47%',
    borderWidth: 1,
    alignItems: 'center',
  },
  actionIcon: { fontSize: 32, marginBottom: 8 },
  actionTitle: { color: '#fff', fontSize: 14, fontWeight: '500' },
});
