import os
import sys

# Asegurar que la raíz de apps/api esté en sys.path para todos los tests
api_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if api_root not in sys.path:
    sys.path.insert(0, api_root)
