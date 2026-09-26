import { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { api } from "./src/lib/api";
import { unwrap, ApiError } from "@repo/api-client";

export default function App() {
  const [status, setStatus] = useState("Cargando...");

  useEffect(() => {
    let mounted = true;

    api
      .GET("/health")
      .then((result) => {
        if (!mounted) return;

        try {
          const health = unwrap(result);
          setStatus(`${health.status} — ${health.service} — ${health.version}`);
        } catch (error) {
          if (error instanceof ApiError) {
            setStatus(`Error ${error.status}: ${error.message}`);
          } else {
            setStatus(`Error: ${String(error)}`);
          }
        }
      })
      .catch((error) => {
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
