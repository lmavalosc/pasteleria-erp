import { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { getHealth, type HealthResponse } from "@pasteleria/api-client";
import { api } from "./src/lib/api";

export default function App() {
  const [status, setStatus] = useState("Cargando...");

  useEffect(() => {
    let mounted = true;

    getHealth({ client: api })
      .then((result) => {
        if (!mounted) return;

        if (result.data) {
          const health = result.data as unknown as HealthResponse;
          setStatus(`${health.status} — ${health.service} — ${health.version}`);
        } else if (result.error) {
          setStatus(`Error: ${JSON.stringify(result.error)}`);
        }
      })
      .catch((error: unknown) => {
        if (!mounted) return;
        setStatus(`Excepción: ${String(error)}`);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Paso 2 — Contrato OpenAPI conectado a Mobile</Text>
      <Text style={styles.status}>{status}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
  title: {
    fontSize: 20,
    fontWeight: "700",
    marginBottom: 16,
    textAlign: "center",
  },
  status: {
    fontSize: 16,
    textAlign: "center",
  },
});
