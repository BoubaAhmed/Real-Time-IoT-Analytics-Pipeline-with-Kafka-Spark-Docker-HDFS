# Real-Time IoT Analytics Pipeline with Kafka, Spark, Docker, and HDFS

![IoT Pipeline](https://img.shields.io/badge/IoT-Real--Time--Analytics-blue) ![Kafka](https://img.shields.io/badge/Apache-Kafka-orange) ![Spark](https://img.shields.io/badge/Apache-Spark-red) ![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen) ![HDFS](https://img.shields.io/badge/HDFS-Storage-yellow)

🎉 Bienvenue dans le projet **Real-Time IoT Analytics Pipeline** ! Ce projet met en œuvre une architecture robuste pour le traitement des données en temps réel à l'aide des technologies modernes comme Kafka, Spark Streaming, HDFS, et Docker. Une interface web Flask est utilisée pour visualiser les données traitées.

---

## 📌 **Description**

Ce projet est conçu pour démontrer comment :
- **Collecter** des données en temps réel à partir de capteurs IoT ou d'autres sources.
- **Traiter** ces données en temps réel avec Apache Spark Streaming.
- **Stocker** les données transformées dans HDFS pour une analyse ultérieure.
- **Visualiser** les flux de données et les résultats dans une interface web conviviale.

### **Exemple de scénario d'utilisation**
Imaginez un réseau de capteurs surveillant la température et l'humidité dans une usine. Les données transmises sont collectées en temps réel par Kafka, analysées via Spark Streaming (ex. identification d'anomalies), stockées dans HDFS, puis affichées dans un tableau de bord interactif.

---

## 🛠️ **Technologies Utilisées**
Voici les principales technologies utilisées dans ce projet :
| Tech | Description |
|------|-------------|
| **Apache Kafka** | Collecte et transmet les données en temps réel. |
| **Apache Spark Streaming** | Traitement des flux de données en temps réel. |
| **HDFS** | Stockage distribué pour les données traitées. |
| **Docker** | Conteneurisation des différents services pour un déploiement simplifié. |
| **Flask** | Interface web pour la visualisation des données. |

---

## 🚀 **Fonctionnalités**
- **Traitement des données en temps réel** : Analyse des flux de données en continu.
- **Stockage distribué** : Conservation des données traitées pour des analyses futures.
- **Visualisation intuitive** : Affichage des données en temps réel à l'aide de graphiques et tableaux.
- **Extensibilité** : Facile à adapter pour des cas d'utilisation spécifiques (IoT, industrie, santé, etc.).

---

## 📂 **Structure du Projet**
```plaintext
📁 Real-Time-IoT-Analytics-Pipeline
├── 📂 kafka/                # Configuration et scripts Kafka.
├── 📂 spark/                # Scripts de traitement Spark Streaming.
├── 📂 hdfs/                 # Configuration pour le stockage HDFS.
├── 📂 docker/               # Fichiers Docker pour chaque service.
├── 📂 flask_app/            # Application Flask pour la visualisation.
├── 📂 data/                 # Données d'entrée et de test.
├── 📜 docker-compose.yml    # Fichier Docker Compose pour démarrer l'ensemble du pipeline.
└── 📜 README.md             # Documentation du projet.
```

---

## 🔧 **Installation et Configuration**

### **Prérequis**
- Docker et Docker Compose installés
- Python 3.7+ installé

### **Étapes pour exécuter le projet**
1. **Clonez le dépôt** :
   ```bash
   git clone https://github.com/BoubaAhmed/Real-Time-IoT-Analytics-Pipeline-with-Kafka-Spark-Docker-HDFS.git
   cd Real-Time-IoT-Analytics-Pipeline-with-Kafka-Spark-Docker-HDFS
   ```

2. **Lancez les conteneurs Docker** :
   ```bash
   docker-compose up --build
   ```

3. **Accédez à l'interface Flask** :
   - Ouvrez votre navigateur et allez à [http://localhost:5000](http://localhost:5000).

4. **Testez avec des données d'exemple** :
   - Envoyez des données vers Kafka à l'aide des scripts fournis dans le dossier `kafka/`.

---

## 📊 **Visualisation des Données**
L'application Flask offre une interface utilisateur simple et intuitive pour :
- Suivre les données des capteurs en temps réel.
- Visualiser des graphiques et des tableaux.
- Configurer des alertes pour des seuils personnalisés.

---

## 🛡️ **Contributions**
Les contributions sont les bienvenues ! Si vous souhaitez améliorer ce projet ou ajouter de nouvelles fonctionnalités :
1. **Forkez** le dépôt.
2. Créez une branche pour vos modifications :
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   ```
3. Soumettez une Pull Request 🎉.

---

## 📄 **Licence**
Ce projet est sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.

---

## 📞 **Contact**
Pour toute question ou suggestion, n'hésitez pas à me contacter via [GitHub](https://github.com/BoubaAhmed).

---

🌟 **Si vous aimez ce projet, n'oubliez pas de lui donner une étoile ⭐ sur GitHub !**