# Centres vétérinaires — site web Flask + PostgreSQL

Projet de L2 (Bases de données), réalisé en binôme sur environ 3 mois.

Site web pour une association fictive de centres vétérinaires d'Île-de-France :
consultation des centres et de leurs spécialités, suivi médical des animaux,
ordonnances, vaccins et espace réservé au personnel.

## Technologies
Python (Flask), PostgreSQL (psycopg2), HTML5 / CSS3 (templates Jinja).

## Fonctionnalités
**Particuliers**
- liste des centres, triée par ville ou par spécialité, et page de détail d'un centre
- recherche d'un centre par spécialité
- espace propriétaire : historique de l'animal et état de ses vaccins

**Personnel**
- connexion par login / mot de passe
- ajout d'animaux, de propriétaires, de soins, d'ordonnances et de vaccins
- historique médical global avec recherche, vue des centres et de leurs employés

## Base de données
12 tables (Animal, Proprietaire, Possede, Employe, Centre_veterinaire, Travail,
Ordonnance, Contient, Medicament, Vaccin, Operation, Est_dans) avec des données
de test dans `dump.sql` (toutes fictives).

## Lancer le projet
```bash
pip install flask psycopg2-binary
createdb veterinaire
psql veterinaire < dump.sql

export DB_NAME=veterinaire
export DB_USER=<votre_utilisateur>
export DB_PASSWORD=<votre_mot_de_passe>
export DB_HOST=localhost

flask --app main run
```

## Ma part
Requêtes SQL et templates des pages web.
