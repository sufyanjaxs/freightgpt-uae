import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import NavigationScreen from './src/screens/NavigationScreen';
import DocumentUploadScreen from './src/screens/DocumentUploadScreen';
import ProfileScreen from './src/screens/ProfileScreen';

export type RootStackParamList = {
  Login: undefined;
  Home: undefined;
  Navigation: { tripId: string };
  DocumentUpload: { tripId?: string };
  Profile: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

function App(): React.JSX.Element {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Login"
          screenOptions={{
            headerStyle: { backgroundColor: '#1e40af' },
            headerTintColor: '#fff',
            headerTitleStyle: { fontWeight: 'bold' },
          }}>
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen
            name="Home"
            component={HomeScreen}
            options={{ title: 'FreightGPT Driver' }}
          />
          <Stack.Screen
            name="Navigation"
            component={NavigationScreen}
            options={{ title: 'Navigation' }}
          />
          <Stack.Screen
            name="DocumentUpload"
            component={DocumentUploadScreen}
            options={{ title: 'Upload Document' }}
          />
          <Stack.Screen
            name="Profile"
            component={ProfileScreen}
            options={{ title: 'My Profile' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

export default App;
