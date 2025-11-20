import os
import subprocess
import json
import yaml

# Chemins fichiers/dossiers
k6_path = r"C:\Program Files\k6\k6.exe"
test_script = r".\tests\test_k6.js"
json_output = r".\tests\test_k6.json"
yaml_output = r".\tests\test_k6.yaml"

# Création du dossier ./tests s’il n’existe pas (probablement déjà présent)
os.makedirs(os.path.dirname(json_output), exist_ok=True)

# Lancer k6 pour générer le JSON
print("Exécution de k6 pour générer le fichier JSON...")
result = subprocess.run([k6_path, "run", f"--out=json={json_output}", test_script],
                        capture_output=True, text=True)

if result.returncode != 0:
    print("Erreur lors de l'exécution de k6 :")
    print(result.stderr)
    exit(1)
else:
    print("k6 exécuté avec succès.")

# Lecture du JSON ligne par ligne (NDJSON)
print("Lecture du fichier JSON et conversion en YAML...")
data_list = []
with open(json_output, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                data_list.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Erreur JSONDecode sur une ligne: {e}")
                exit(1)

# Écriture du YAML dans ./tests/
with open(yaml_output, 'w', encoding='utf-8') as f:
    yaml.dump(data_list, f, allow_unicode=True)

print(f"Conversion réussie :\n- JSON généré : {json_output}\n- YAML généré : {yaml_output}")