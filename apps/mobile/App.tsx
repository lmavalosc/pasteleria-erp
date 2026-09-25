import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  SafeAreaView,
  StatusBar,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { apiClient, API_BASE_URL, TENANT_ID } from './src/api';

type Tab = 'welcome' | 'catalog' | 'expenses';

interface HealthData {
  status: string;
  service: string;
  tenant_id: string;
  timestamp: string;
}

export default function App() {
  const [currentTab, setCurrentTab] = useState<Tab>('welcome');
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(true);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealthStatus();
  }, []);

  const fetchHealthStatus = async () => {
    setLoadingHealth(true);
    setConnectionError(null);
    try {
      const { data, error } = await apiClient.GET('/health');
      if (error || !data) {
        setConnectionError('El backend no respondió satisfactoriamente');
        setHealth({
          status: 'error',
          service: 'FastAPI Offline',
          tenant_id: TENANT_ID,
          timestamp: new Date().toISOString(),
        });
      } else {
        setHealth(data as HealthData);
      }
    } catch (err: any) {
      setConnectionError(err?.message || 'Error de conexión');
      setHealth({
        status: 'offline',
        service: 'FastAPI Service (Local Fallback)',
        tenant_id: TENANT_ID,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoadingHealth(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFF9F2" />

      {/* Header Superior */}
      <View style={styles.header}>
        <View style={styles.brandRow}>
          <Text style={styles.brandIcon}>🍰</Text>
          <View>
            <Text style={styles.brandTitle}>Maison du Délice</Text>
            <Text style={styles.brandSubtitle}>ATELIER MOBILE • FASE 1</Text>
          </View>
        </View>
      </View>

      {/* Contenido Principal por Pestaña */}
      <View style={styles.main}>
        {currentTab === 'welcome' && (
          <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
            <View style={styles.welcomeBanner}>
              <Text style={styles.welcomeTag}>TERMINAL OPERATIVO</Text>
              <Text style={styles.welcomeHeading}>Bienvenido al Atelier Móvil</Text>
              <Text style={styles.welcomeDesc}>
                Sistema conectado mediante cliente OpenAPI tipado con soporte de partida doble, bóveda documental y costeo técnico.
              </Text>
            </View>

            {/* Widget de Estado de Conexión /health */}
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>Conexión con FastAPI Backend</Text>
                {loadingHealth ? (
                  <ActivityIndicator size="small" color="#D4AF37" />
                ) : (
                  <View style={[styles.badge, health?.status === 'ok' ? styles.badgeSuccess : styles.badgeWarning]}>
                    <Text style={[styles.badgeText, health?.status === 'ok' ? styles.badgeTextSuccess : styles.badgeTextWarning]}>
                      {health?.status.toUpperCase()}
                    </Text>
                  </View>
                )}
              </View>

              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Host Backend:</Text>
                <Text style={styles.infoValue}>{API_BASE_URL}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Tenant Activo:</Text>
                <Text style={[styles.infoValue, { color: '#D4AF37', fontWeight: 'bold' }]}>
                  {health?.tenant_id || TENANT_ID}
                </Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Servicio:</Text>
                <Text style={styles.infoValue}>{health?.service || 'Cargando...'}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Timestamp:</Text>
                <Text style={styles.infoValueSmall}>{health?.timestamp || '---'}</Text>
              </View>

              <TouchableOpacity style={styles.refreshButton} onPress={fetchHealthStatus}>
                <Text style={styles.refreshButtonText}>↻ Reintentar Health Check</Text>
              </TouchableOpacity>
            </View>

            {/* Accesos Directos a Vistas Futuras */}
            <Text style={styles.sectionTitle}>Módulos Preparados</Text>

            <TouchableOpacity style={styles.navCard} onPress={() => setCurrentTab('catalog')}>
              <Text style={styles.navCardIcon}>🥐</Text>
              <View style={styles.navCardContent}>
                <Text style={styles.navCardTitle}>Catálogo & Pedidos</Text>
                <Text style={styles.navCardDesc}>Consulta de alta pastelería y seguimiento de órdenes</Text>
              </View>
              <Text style={styles.navCardArrow}>→</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.navCard} onPress={() => setCurrentTab('expenses')}>
              <Text style={styles.navCardIcon}>📸</Text>
              <View style={styles.navCardContent}>
                <Text style={styles.navCardTitle}>Récord Rápido de Gastos</Text>
                <Text style={styles.navCardDesc}>Rendición fotográfica de boletas y compras de insumos</Text>
              </View>
              <Text style={styles.navCardArrow}>→</Text>
            </TouchableOpacity>
          </ScrollView>
        )}

        {/* 1. Catálogo / Mis Pedidos */}
        {currentTab === 'catalog' && (
          <ScrollView contentContainerStyle={styles.scrollContent}>
            <View style={styles.viewHeader}>
              <Text style={styles.viewTitle}>Catálogo & Mis Pedidos</Text>
              <Text style={styles.viewDesc}>
                Conexión lista con los endpoints de catálogo y órdenes del backend.
              </Text>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardSectionHeading}>Colección en Vitrina</Text>
              {[
                { name: 'Ópera Clásica de París', price: '$18.500 CLP', note: 'Chocolate 70% & Café Arábica' },
                { name: 'Tarta de Frambuesas & Pistacho', price: '$16.900 CLP', note: 'Pistacho de Sicilia' },
                { name: 'Eclair de Vainilla Bourbon', price: '$4.200 CLP', note: 'Vainilla natural de Madagascar' },
              ].map((item, idx) => (
                <View key={idx} style={styles.catalogItem}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.catalogItemName}>{item.name}</Text>
                    <Text style={styles.catalogItemNote}>{item.note}</Text>
                  </View>
                  <Text style={styles.catalogItemPrice}>{item.price}</Text>
                </View>
              ))}
            </View>
          </ScrollView>
        )}

        {/* 2. Récord Rápido de Gastos (Foto boleta/insumos) */}
        {currentTab === 'expenses' && (
          <ScrollView contentContainerStyle={styles.scrollContent}>
            <View style={styles.viewHeader}>
              <Text style={styles.viewTitle}>Récord Rápido de Gastos</Text>
              <Text style={styles.viewDesc}>
                Flujo móvil para rendir compras de materias primas adjuntando foto del comprobante a la bóveda digital.
              </Text>
            </View>

            <View style={styles.card}>
              <View style={styles.photoPlaceholder}>
                <Text style={styles.photoIcon}>📷</Text>
                <Text style={styles.photoText}>Subir Foto de Boleta / Factura</Text>
                <Text style={styles.photoSubtext}>
                  Listo para integrar Expo ImagePicker y cámara de dispositivo
                </Text>
              </View>

              <View style={styles.formDummy}>
                <Text style={styles.inputDummyLabel}>Proveedor:</Text>
                <View style={styles.inputDummyBox}>
                  <Text style={styles.inputDummyText}>Ej: Molinos del Sur SpA</Text>
                </View>

                <Text style={styles.inputDummyLabel}>Monto Total (CLP):</Text>
                <View style={styles.inputDummyBox}>
                  <Text style={styles.inputDummyText}>Ej: $45.000</Text>
                </View>

                <Text style={styles.inputDummyLabel}>Categoría de Insumo:</Text>
                <View style={styles.inputDummyBox}>
                  <Text style={styles.inputDummyText}>Materias Primas (Harinas / Lácteos)</Text>
                </View>

                <TouchableOpacity style={styles.submitDummyBtn} activeOpacity={0.8}>
                  <Text style={styles.submitDummyBtnText}>Guardar Gasto en Bóveda</Text>
                </TouchableOpacity>
              </View>
            </View>
          </ScrollView>
        )}
      </View>

      {/* Navegación Inferior (Tabs) */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setCurrentTab('welcome')}
        >
          <Text style={styles.bottomNavIcon}>🏠</Text>
          <Text style={[styles.bottomNavText, currentTab === 'welcome' && styles.bottomNavTextActive]}>
            Inicio
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setCurrentTab('catalog')}
        >
          <Text style={styles.bottomNavIcon}>🥐</Text>
          <Text style={[styles.bottomNavText, currentTab === 'catalog' && styles.bottomNavTextActive]}>
            Catálogo
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setCurrentTab('expenses')}
        >
          <Text style={styles.bottomNavIcon}>🧾</Text>
          <Text style={[styles.bottomNavText, currentTab === 'expenses' && styles.bottomNavTextActive]}>
            Rendir Gastos
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF9F2',
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#E8DFD5',
    backgroundColor: '#FFF9F2',
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  brandIcon: {
    fontSize: 26,
  },
  brandTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#231610',
  },
  brandSubtitle: {
    fontSize: 9,
    letterSpacing: 2,
    color: '#D4AF37',
    fontWeight: '700',
  },
  main: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 90,
  },
  welcomeBanner: {
    backgroundColor: '#231610',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
  },
  welcomeTag: {
    color: '#D4AF37',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: 6,
  },
  welcomeHeading: {
    color: '#FFF9F2',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 6,
  },
  welcomeDesc: {
    color: '#B3A196',
    fontSize: 12,
    lineHeight: 18,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E8DFD5',
    marginBottom: 20,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F7EEE3',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#231610',
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  badgeSuccess: {
    backgroundColor: '#E8F5E9',
    borderColor: '#C8E6C9',
    borderWidth: 1,
  },
  badgeWarning: {
    backgroundColor: '#FFF3E0',
    borderColor: '#FFE0B2',
    borderWidth: 1,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
  },
  badgeTextSuccess: {
    color: '#2E7D32',
  },
  badgeTextWarning: {
    color: '#E65100',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  infoLabel: {
    fontSize: 12,
    color: '#7D7068',
  },
  infoValue: {
    fontSize: 12,
    color: '#231610',
    fontWeight: '500',
  },
  infoValueSmall: {
    fontSize: 10,
    color: '#7D7068',
    fontFamily: 'monospace',
  },
  refreshButton: {
    marginTop: 14,
    paddingVertical: 10,
    backgroundColor: '#F7EEE3',
    borderRadius: 10,
    alignItems: 'center',
  },
  refreshButtonText: {
    color: '#231610',
    fontSize: 12,
    fontWeight: '600',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#231610',
    marginBottom: 12,
  },
  navCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E8DFD5',
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  navCardIcon: {
    fontSize: 24,
    marginRight: 14,
  },
  navCardContent: {
    flex: 1,
  },
  navCardTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#231610',
    marginBottom: 2,
  },
  navCardDesc: {
    fontSize: 11,
    color: '#7D7068',
  },
  navCardArrow: {
    fontSize: 16,
    color: '#D4AF37',
    fontWeight: '700',
  },
  viewHeader: {
    marginBottom: 16,
  },
  viewTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#231610',
    marginBottom: 4,
  },
  viewDesc: {
    fontSize: 12,
    color: '#7D7068',
    lineHeight: 18,
  },
  cardSectionHeading: {
    fontSize: 15,
    fontWeight: '700',
    color: '#231610',
    marginBottom: 12,
  },
  catalogItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F7EEE3',
  },
  catalogItemName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#231610',
  },
  catalogItemNote: {
    fontSize: 11,
    color: '#7D7068',
    marginTop: 2,
  },
  catalogItemPrice: {
    fontSize: 14,
    fontWeight: '700',
    color: '#D4AF37',
  },
  photoPlaceholder: {
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: '#E8DFD5',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    backgroundColor: '#FFF9F2',
    marginBottom: 16,
  },
  photoIcon: {
    fontSize: 32,
    marginBottom: 6,
  },
  photoText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#231610',
  },
  photoSubtext: {
    fontSize: 10,
    color: '#7D7068',
    marginTop: 2,
    textAlign: 'center',
  },
  formDummy: {
    gap: 8,
  },
  inputDummyLabel: {
    fontSize: 12,
    color: '#7D7068',
    fontWeight: '500',
  },
  inputDummyBox: {
    backgroundColor: '#F7EEE3',
    padding: 12,
    borderRadius: 8,
    marginBottom: 6,
  },
  inputDummyText: {
    fontSize: 12,
    color: '#7D7068',
  },
  submitDummyBtn: {
    backgroundColor: '#231610',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 8,
  },
  submitDummyBtnText: {
    color: '#FFF9F2',
    fontSize: 13,
    fontWeight: '700',
  },
  bottomNav: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 64,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E8DFD5',
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  navItem: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 4,
  },
  bottomNavIcon: {
    fontSize: 20,
    marginBottom: 2,
  },
  bottomNavText: {
    fontSize: 10,
    color: '#7D7068',
    fontWeight: '500',
  },
  bottomNavTextActive: {
    color: '#D4AF37',
    fontWeight: '700',
  },
});
