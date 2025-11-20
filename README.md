# Qualité Logicielle

Ce projet est dédié à la mise en place et au suivi des bonnes pratiques de **qualité logicielle** dans le cadre du projet DigiCheese.  
Il contient les ressources, scripts et pipelines nécessaires pour assurer la maintenabilité, la robustesse et la conformité du code.

---

## Objectifs
- Mettre en place un pipeline CI/CD automatisé.
- Vérifier la qualité du code avec **flake8**.
- Exécuter les tests unitaires avec **pytest**.
- Documenter les pratiques et outils de qualité logicielle.

---

## Pipeline CI/CD

Le pipeline est défini dans `.github/workflows/quality_pipeline.yml` et s’exécute automatiquement sur chaque **push** dans la branche `main`.

### Badge de statut

![QualityPipeline](https://github.com/PhilippeVita/Qualite_Logicielle/actions/workflows/quality_pipeline.yml/badge.svg)

---

## Structure du projet

Qualite_Logicielle/ 
```
│ 
├── app/ # Code applicatif 
├── tests/ # Tests unitaires 
├── documentation/ # Ressources et fiches techniques 
└── .github/workflows/ # Pipelines CI/CD
```


## Exécution locale

Pour tester localement :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
flake8 app.py
```

## Résultat attendu
- Le badge GitHub Actions affichera en temps réel l’état du pipeline.  
- Le README servira de **point d’entrée clair** pour tout collaborateur ou auditeur qualité.  
- Tu réponds aux exigences du TP3 : dépôt séparé, pipeline opérationnel, documentation initiale.

---
