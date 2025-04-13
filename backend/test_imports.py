import sys
sys.path.append("/home/fatima/feeling_Project/backend")  # Chemin absolu

try:
    from core.settings import DEBUG  # Changé de 'backend.settings' à 'core.settings'
    import rest_framework
    print("✓ Import réussi ! DEBUG =", DEBUG)
except Exception as e:
    print("❌ Erreur :", e)
    print("Python path:", sys.path)