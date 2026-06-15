import React, { useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, Image, Alert, ActivityIndicator
} from 'react-native';
import DocumentPicker from 'react-native-document-picker';
import { documentsApi } from '../services/api';

export default function DocumentUploadScreen({ route }: any) {
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const [docType, setDocType] = useState('pod');

  const documentTypes = [
    { id: 'pod', label: 'Proof of Delivery', icon: '📋' },
    { id: 'bol', label: 'Bill of Lading', icon: '📄' },
    { id: 'invoice', label: 'Invoice', icon: '🧾' },
    { id: 'other', label: 'Other', icon: '📁' },
  ];

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.pdf, DocumentPicker.types.images],
      });
      setSelectedFile(result[0]);
    } catch (err) {
      if (!DocumentPicker.isCancel(err)) {
        Alert.alert('Error', 'Failed to pick document');
      }
    }
  };

  const uploadDocument = async () => {
    if (!selectedFile) {
      Alert.alert('Error', 'Please select a file first');
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: selectedFile.uri,
        type: selectedFile.type,
        name: selectedFile.name,
      } as any);
      formData.append('document_type', docType);
      if (route.params?.tripId) {
        formData.append('load_id', route.params.tripId);
      }
      await documentsApi.upload(formData);
      Alert.alert('Success', 'Document uploaded successfully');
      setSelectedFile(null);
    } catch (err) {
      Alert.alert('Error', 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Select Document Type</Text>
      <View style={styles.typeGrid}>
        {documentTypes.map((type) => (
          <TouchableOpacity
            key={type.id}
            style={[styles.typeCard, docType === type.id && styles.typeCardSelected]}
            onPress={() => setDocType(type.id)}>
            <Text style={styles.typeIcon}>{type.icon}</Text>
            <Text style={styles.typeLabel}>{type.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity style={styles.pickButton} onPress={pickDocument}>
        <Text style={styles.pickButtonText}>
          {selectedFile ? selectedFile.name : '📎 Pick Document'}
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.uploadButton, uploading && styles.uploadButtonDisabled]}
        onPress={uploadDocument}
        disabled={uploading || !selectedFile}>
        {uploading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.uploadButtonText}>Upload Document</Text>
        )}
      </TouchableOpacity>

      {selectedFile && (
        <View style={styles.fileInfo}>
          <Text style={styles.fileInfoText}>
            File: {selectedFile.name}
          </Text>
          <Text style={styles.fileInfoText}>
            Size: {(selectedFile.size / 1024).toFixed(1)} KB
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a', padding: 16 },
  title: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginBottom: 16 },
  typeGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 24 },
  typeCard: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    width: '47%',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#334155',
  },
  typeCardSelected: { borderColor: '#2563eb', backgroundColor: '#1e3a5f' },
  typeIcon: { fontSize: 28, marginBottom: 8 },
  typeLabel: { color: '#fff', fontSize: 12, fontWeight: '500', textAlign: 'center' },
  pickButton: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#334155',
    marginBottom: 16,
  },
  pickButtonText: { color: '#94a3b8', fontSize: 16 },
  uploadButton: {
    backgroundColor: '#2563eb',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  uploadButtonDisabled: { opacity: 0.6 },
  uploadButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  fileInfo: { marginTop: 16, backgroundColor: '#1e293b', borderRadius: 12, padding: 12 },
  fileInfoText: { color: '#94a3b8', fontSize: 14, marginBottom: 4 },
});
