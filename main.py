from flask import Flask, render_template, request, redirect, url_for, flash,session
from db import connect
import datetime
app = Flask(__name__)
app.secret_key = 'votre_clé_secrète'

# Page d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html')


# Historique médical d'un animal
@app.route('/historique_animal/<int:animal_id>', methods=['GET'])
def historique_animal(animal_id):
    query = """
    SELECT v.date, v.nom
    FROM Vaccin v
    WHERE v.animalid = %s
    """
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (animal_id,))
            historique = cur.fetchall()

    return render_template('historique_animal.html', historique=historique)


# Connexion particuliers
@app.route('/connexion_particuliers', methods=['GET', 'POST'])
def connexion_particuliers():
    if request.method == 'POST':
        nom = request.form['nom']
        animal_id = request.form['animal_id']

        query = """
        SELECT p.ProprietaireID, p.Nom, p.Prenom
        FROM Proprietaire p
        JOIN Possede pos ON p.ProprietaireID = pos.ProprietaireID
        WHERE pos.AnimalID = %s AND p.Nom = %s
        """
        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (animal_id, nom))
                    proprietaire = cur.fetchone()

            if proprietaire:
                flash(f"Bienvenue, {proprietaire[1]} {proprietaire[2]} !", "success")
                # Redirigez avec le proprietaire_id
                return redirect(url_for('espace_particulier', proprietaire_id=proprietaire[0]))
            else:
                flash("Nom ou numéro de suivi incorrect.", "error")
                return redirect(url_for('connexion_particuliers'))

        except Exception as e:
            flash(f"Erreur lors de la connexion : {e}", "error")
            return redirect(url_for('connexion_particuliers'))

    return render_template('connexion_particuliers.html')




# Connexion personnel
@app.route('/connexion_personnel', methods=['GET', 'POST'])
def connexion_personnel():
    if request.method == 'POST':
        login = request.form['login']
        mdp = request.form['mdp']
        query = "SELECT * FROM Employe WHERE login = %s AND mot_de_passe = %s"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (login, mdp))
                employe = cur.fetchone()

        if employe:
            return redirect(url_for('espace_personnel'))
        else:
            flash("Identifiant ou mot de passe incorrect.")
            return redirect(url_for('connexion_personnel'))
    return render_template('connexion_personnel.html')

@app.route('/espace_personnel', methods=['GET'])
def espace_personnel():
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                # Récupérer les gérants des centres
                query_gerant = """
                SELECT c.nom AS nom_centre, e.nom AS nom_gerant, e.prenom AS prenom_gerant
                FROM Centre_veterinaire c
                JOIN Employe e ON c.EmpID = e.EmpID;
                """
                cur.execute(query_gerant)
                gerants = cur.fetchall()

                # Récupérer la fiche des animaux inscrits
                query_animaux = """
                SELECT a.AnimalID, a.nom AS nom_animal, a.espece, a.age, a.date_inscrit, c.nom AS nom_centre, 
                       p.nom AS proprietaire_nom, p.prenom AS proprietaire_prenom
                FROM Animal a
                LEFT JOIN Est_dans ed ON a.AnimalID = ed.AnimalID
                LEFT JOIN Centre_veterinaire c ON ed.CentreID = c.CentreID
                LEFT JOIN Possede pos ON a.AnimalID = pos.AnimalID
                LEFT JOIN Proprietaire p ON pos.ProprietaireID = p.ProprietaireID;
                """
                cur.execute(query_animaux)
                animaux = cur.fetchall()

        return render_template(
            'espace_personnel.html',
            gerants=gerants,
            animaux=animaux,
        )
    except Exception as e:
        flash(f"Erreur lors de la récupération des données : {e}", "error")
        return redirect(url_for('connexion_personnel'))




@app.route('/ajouter_animal', methods=['GET', 'POST'])
def ajouter_animal():
    if request.method == 'POST':
        # Récupération des données
        nom = request.form['nom']
        espece = request.form['espece']
        age = request.form['age']
        sexe = request.form['sexe']
        signe_distinct = request.form['signe_distinct']
        proprietaire_id = request.form['proprietaire_id']
        centre_id = request.form['centre_id']  # Récupération de l'ID du centre

        # Requêtes SQL
        query_check_owner = "SELECT COUNT(*) FROM Proprietaire WHERE proprietaireid = %s"
        query_check_centre = "SELECT COUNT(*) FROM Centre_veterinaire WHERE centreid = %s"
        query_animal = """
        INSERT INTO Animal (nom, espece, age, sexe, signe_distinct, date_inscrit)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
        RETURNING animalid
        """
        query_possede = """
        INSERT INTO Possede (proprietaireid, animalid)
        VALUES (%s, %s)
        """
        query_est_dans = """
        INSERT INTO Est_dans (animalid, centreid)
        VALUES (%s, %s)
        """

        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    # Vérifier si le propriétaire existe
                    cur.execute(query_check_owner, (proprietaire_id,))
                    owner_exists = cur.fetchone()[0] > 0
                    if not owner_exists:
                        flash("Erreur : Le propriétaire n'existe pas.", "error")
                        return redirect(url_for('ajouter_animal'))

                    # Vérifier si le centre existe
                    cur.execute(query_check_centre, (centre_id,))
                    centre_exists = cur.fetchone()[0] > 0
                    if not centre_exists:
                        flash("Erreur : Le centre n'existe pas.", "error")
                        return redirect(url_for('ajouter_animal'))

                    # Ajouter l'animal
                    cur.execute(query_animal, (nom, espece, age, sexe, signe_distinct))
                    animal_id = cur.fetchone()[0]

                    # Associer l'animal au propriétaire
                    cur.execute(query_possede, (proprietaire_id, animal_id))

                    # Associer l'animal au centre
                    cur.execute(query_est_dans, (animal_id, centre_id))

                conn.commit()
                flash("L'animal a été ajouté avec succès !", "success")
                return redirect(url_for('espace_personnel'))

        except Exception as e:
            if "animal_age_check" in str(e):
                flash("Erreur : L'âge de l'animal ne peut pas être négatif.", "error")
            elif "possede_proprietaireid_fkey" in str(e):
                flash("Erreur : Le propriétaire n'existe pas.", "error")
            else:
                flash(f"Erreur inattendue : {e}", "error")
            return redirect(url_for('ajouter_animal'))

    # Récupérer la liste des propriétaires et des centres pour les menus déroulants
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT ProprietaireID, nom, prenom FROM Proprietaire")
                proprietaires = cur.fetchall()
                cur.execute("SELECT CentreID, nom FROM Centre_veterinaire")
                centres = cur.fetchall()
    except Exception as e:
        flash(f"Erreur : {e}", "error")
        proprietaires = []
        centres = []

    return render_template('ajouter_animal.html', proprietaires=proprietaires, centres=centres)






# Ajouter une ordonnance
@app.route('/ajouter_ordonnance', methods=['GET', 'POST'])
def ajouter_ordonnance():
    if request.method == 'POST':
        animal_id = request.form['animal_id']
        date_ordonnance = request.form['date_ordonnance']
        medicament_ids = request.form.getlist('medicament_ids')
        emp_id = request.form['emp_id']  # Récupérer l'employé sélectionné

        # Requête pour insérer l'ordonnance
        query_ordonnance = """
        INSERT INTO Ordonnance (dateordo, AnimalID, EmpID)
        VALUES (%s, %s, %s)
        RETURNING OrdoID
        """
        # Requête pour insérer les médicaments associés
        query_contient = """
        INSERT INTO Contient (OrdoID, MedocID)
        VALUES (%s, %s)
        """

        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    # Ajouter l'ordonnance
                    cur.execute(query_ordonnance, (date_ordonnance, animal_id, emp_id))
                    ordo_id = cur.fetchone()[0]

                    # Associer les médicaments sélectionnés
                    for med_id in medicament_ids:
                        cur.execute(query_contient, (ordo_id, med_id))
                
                conn.commit()
            flash("Ordonnance ajoutée avec succès !", "success")
            return redirect(url_for('espace_personnel'))

        except Exception as e:
            flash(f"Erreur lors de l'ajout de l'ordonnance : {e}", "error")
            return redirect(url_for('ajouter_ordonnance'))

    # Récupérer la liste des animaux et des médicaments pour le formulaire
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT AnimalID, nom FROM Animal")
                animaux = cur.fetchall()
                cur.execute("SELECT MedocID, nom FROM Medicament")
                medicaments = cur.fetchall()
                cur.execute("SELECT EmpID, nom, prenom FROM Employe")
                employes = cur.fetchall()
    except Exception as e:
        flash(f"Erreur lors de la récupération des données : {e}", "error")
        animaux, medicaments, employes = [], [], []

    return render_template('ajouter_ordonnance.html', animaux=animaux, medicaments=medicaments, employes=employes)









@app.route('/verifier_animaux', methods=['GET'])
def verifier_animaux():
    query = "SELECT * FROM Animal"
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                animaux = cur.fetchall()
        return {"animaux": animaux}
    except Exception as e:
        return {"erreur": str(e)}

from flask import render_template, flash, redirect, url_for
import datetime
from db import connect

@app.route('/espace_particulier/<int:proprietaire_id>', methods=['GET'])
def espace_particulier(proprietaire_id):
    try:
        # Récupérer les informations des animaux du propriétaire
        query_animaux = """
        SELECT a.AnimalID, a.nom, a.espece, a.age, a.sexe, COALESCE(a.signe_distinct, 'Aucun')
        FROM Animal a
        JOIN Possede p ON a.AnimalID = p.AnimalID
        WHERE p.ProprietaireID = %s
        """
        
        # Récupérer les vaccins de chaque animal
        query_vaccins = """
        SELECT v.nom, v.date, 
               (v.date + INTERVAL '1 month' * v.duree) AS date_rappel, 
               v.AnimalID
        FROM Vaccin v
        WHERE v.AnimalID IN (
            SELECT a.AnimalID
            FROM Animal a
            JOIN Possede p ON a.AnimalID = p.AnimalID
            WHERE p.ProprietaireID = %s
        )
        """
        
        with connect() as conn:
            with conn.cursor() as cur:
                # Récupérer les animaux
                cur.execute(query_animaux, (proprietaire_id,))
                animaux = cur.fetchall()

                # Récupérer les vaccins
                cur.execute(query_vaccins, (proprietaire_id,))
                vaccins = cur.fetchall()

        # Organiser les données des vaccins par animal
        animal_vaccins = {}
        for vaccin in vaccins:
            animal_id = vaccin[3]
            if animal_id not in animal_vaccins:
                animal_vaccins[animal_id] = []
            animal_vaccins[animal_id].append({
                "nom": vaccin[0],
                "date": vaccin[1],
                "date_rappel": vaccin[2],
                "is_up_to_date": vaccin[2].date() >= datetime.date.today()
            })

        # Organiser les données des animaux
        formatted_animaux = []
        for animal in animaux:
            formatted_animaux.append({
                "id": animal[0],
                "nom": animal[1],
                "espece": animal[2],
                "age": animal[3],
                "sexe": animal[4],
                "signe_distinct": animal[5],
                "vaccins": animal_vaccins.get(animal[0], [])
            })

        return render_template('espace_particulier.html', animaux=formatted_animaux)
    except Exception as e:
        flash(f"Erreur lors de la récupération des informations : {e}", "error")
        return redirect(url_for('accueil'))



@app.route('/centres', methods=['GET'])
def afficher_centres():
    specialite = request.args.get('specialite', '').strip()
    ville = request.args.get('ville', '').strip()
    page = int(request.args.get('page', 1))
    centres_par_page = 5

    # Requête pour récupérer les centres
    query = """
    SELECT c.CentreID, c.nom, c.adresse, c.telephone,
           STRING_AGG(DISTINCT e.specialite, ', ') AS specialites
    FROM Centre_veterinaire c
    LEFT JOIN Travail t ON c.CentreID = t.CentreID
    LEFT JOIN Employe e ON t.EmpID = e.EmpID
    WHERE (%s = '' OR c.adresse ILIKE %s)
    AND (%s = '' OR e.specialite ILIKE %s)
    GROUP BY c.CentreID, c.nom, c.adresse, c.telephone
    ORDER BY c.nom
    LIMIT %s OFFSET %s
    """

    # Total des centres pour la pagination
    query_total = """
    SELECT COUNT(DISTINCT c.CentreID)
    FROM Centre_veterinaire c
    LEFT JOIN Travail t ON c.CentreID = t.CentreID
    LEFT JOIN Employe e ON t.EmpID = e.EmpID
    WHERE (%s = '' OR c.adresse ILIKE %s)
    AND (%s = '' OR e.specialite ILIKE %s)
    """

    try:
        with connect() as conn:
            with conn.cursor() as cur:
                # Exécuter la requête pour récupérer les centres
                cur.execute(query, (ville, f"%{ville}%", specialite, f"%{specialite}%",
                                    centres_par_page, (page - 1) * centres_par_page))
                centres = cur.fetchall()

                # Exécuter la requête pour récupérer le nombre total de centres
                cur.execute(query_total, (ville, f"%{ville}%", specialite, f"%{specialite}%"))
                total_centres = cur.fetchone()[0]

        total_pages = (total_centres + centres_par_page - 1) // centres_par_page

        return render_template(
            'centre.html',
            centres=centres,
            page=page,
            total_pages=total_pages,
            ville=ville,
            specialite=specialite
        )
    except Exception as e:
        flash(f"Erreur lors de la récupération des centres : {e}", "error")
        return redirect(url_for('accueil'))






@app.route('/centre/<int:centre_id>', methods=['GET'])
def afficher_centre(centre_id):
    query = """
    SELECT c.nom, 
           c.adresse, 
           c.telephone, 
           e.nom AS directeur_nom, 
           e.prenom AS directeur_prenom
    FROM Centre_veterinaire c
    LEFT JOIN Employe e ON c.EmpID = e.EmpID
    WHERE c.CentreID = %s;
    """
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (centre_id,))
                centre = cur.fetchone()
                
        if centre:
            return render_template('centre_details.html', centre=centre)
        else:
            flash("Centre introuvable.")
            return redirect(url_for('afficher_centres'))
    
    except Exception as e:
        flash(f"Erreur : {e}")
        return redirect(url_for('afficher_centres'))




@app.route('/rechercher_specialite', methods=['GET'])
def rechercher_par_specialite():
    specialite = request.args.get('specialite')  # Récupérer la spécialité depuis les paramètres de la requête

    query = """
    SELECT c.CentreID, c.nom, c.adresse, c.ville, c.telephone, STRING_AGG(DISTINCT e.specialite, ', ') AS specialites
    FROM Centre_veterinaire c
    LEFT JOIN Travail t ON c.CentreID = t.CentreID
    LEFT JOIN Employe e ON t.EmpID = e.EmpID
    WHERE e.specialite ILIKE %s
    GROUP BY c.CentreID
    """
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (f"%{specialite}%",))
            centres = cur.fetchall()

    return render_template('centre.html', centres=centres, specialite=specialite)




@app.route('/ajouter_proprietaire', methods=['GET', 'POST'])
def ajouter_proprietaire():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        prenom = request.form['prenom']
        adresse = request.form['adresse']
        telephone = request.form['telephone']
        email = request.form['email']

        query_proprietaire = """
        INSERT INTO Proprietaire (Nom, Prenom, Adresse, Telephone, Email)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query_proprietaire, (nom, prenom, adresse, telephone, email))
                conn.commit()
            flash("Le propriétaire a été ajouté avec succès !", "success")
            return redirect(url_for('espace_personnel'))
        except Exception as e:
            flash(f"Erreur : {e}", "error")
            return redirect(url_for('ajouter_proprietaire'))

    return render_template('ajouter_proprietaire.html')


@app.route('/ajouter_soin', methods=['GET', 'POST'])
def ajouter_soin():
    if request.method == 'POST':
        date_operation = request.form['date_operation']
        nature_operation = request.form['nature_operation']
        emp_id = request.form['emp_id']
        animal_id = request.form['animal_id']
        centre_id = request.form['centre_id']

        query = """
        INSERT INTO Operation (Date_operation, Nature_operation, EmpID, AnimalID, CentreID)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (date_operation, nature_operation, emp_id, animal_id, centre_id))
                conn.commit()
            flash("Soin ajouté avec succès !", "success")
            return redirect(url_for('espace_personnel'))
        except Exception as e:
            flash(f"Erreur lors de l'ajout du soin : {e}", "error")
            return redirect(url_for('ajouter_soin'))
    
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                # Récupérer la liste des employés
                cur.execute("SELECT EmpID, nom, prenom FROM Employe")
                employes = cur.fetchall()
                # Récupérer la liste des animaux
                cur.execute("SELECT AnimalID, nom FROM Animal")
                animaux = cur.fetchall()
                # Récupérer la liste des centres
                cur.execute("SELECT CentreID, nom FROM Centre_veterinaire")
                centres = cur.fetchall()
        return render_template('ajouter_soin.html', employes=employes, animaux=animaux, centres=centres)
    except Exception as e:
        flash(f"Erreur lors du chargement des données : {e}", "error")
        return redirect(url_for('espace_personnel'))



@app.route('/filtrer_animaux', methods=['GET'])
def filtrer_animaux():
    nom_animal = request.args.get('nom_animal', '').strip()
    nom_centre = request.args.get('nom_centre', '').strip()
    page = int(request.args.get('page', 1))
    animaux_par_page = 5

    query = """
    SELECT a.AnimalID, a.nom AS nom_animal, a.espece, a.age, a.date_inscrit, c.nom AS nom_centre,
           p.nom AS proprietaire_nom, p.prenom AS proprietaire_prenom
    FROM Animal a
    LEFT JOIN Est_dans ed ON a.AnimalID = ed.AnimalID
    LEFT JOIN Centre_veterinaire c ON ed.CentreID = c.CentreID
    LEFT JOIN Possede pos ON a.AnimalID = pos.AnimalID
    LEFT JOIN Proprietaire p ON pos.ProprietaireID = p.ProprietaireID
    WHERE (%s = '' OR a.nom ILIKE %s)
    AND (%s = '' OR c.nom ILIKE %s)
    ORDER BY a.nom
    """

    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (nom_animal, f"%{nom_animal}%", nom_centre, f"%{nom_centre}%"))
                animaux = cur.fetchall()

        # Pagination
        total_animaux = len(animaux)
        total_pages = (total_animaux + animaux_par_page - 1) // animaux_par_page
        animaux = animaux[(page - 1) * animaux_par_page: page * animaux_par_page]

        return render_template(
            'filtrer_animaux.html',
            animaux=animaux,
            nom_animal=nom_animal,
            nom_centre=nom_centre,
            page=page,
            total_pages=total_pages
        )
    except Exception as e:
        flash(f"Erreur lors du filtrage des animaux : {e}", "error")
        return redirect(url_for('espace_personnel'))





@app.route('/historique_global', methods=['GET'])
def historique_global():
    page_ord = int(request.args.get('page_ord', 1))
    page_op = int(request.args.get('page_op', 1))
    items_per_page = 5

    nom_animal = request.args.get('nom_animal', '').strip()
    nom_proprietaire = request.args.get('nom_proprietaire', '').strip()

    try:
        with connect() as conn:
            with conn.cursor() as cur:
                # Requête pour les ordonnances
                query_ord = """
                SELECT o.dateordo, a.nom AS nom_animal, p.nom AS nom_proprietaire,
                       e.nom AS employe_nom, e.specialite, 
                       COALESCE(STRING_AGG(DISTINCT m.nom, ', '), 'Non renseigné') AS medicaments
                FROM Ordonnance o
                LEFT JOIN Animal a ON o.AnimalID = a.AnimalID
                LEFT JOIN Possede pos ON a.AnimalID = pos.AnimalID
                LEFT JOIN Proprietaire p ON pos.ProprietaireID = p.ProprietaireID
                LEFT JOIN Contient c ON o.OrdoID = c.OrdoID
                LEFT JOIN Medicament m ON c.MedocID = m.MedocID
                LEFT JOIN Employe e ON o.EmpID = e.EmpID
                WHERE (%s = '' OR a.nom ILIKE %s) AND (%s = '' OR p.nom ILIKE %s)
                GROUP BY o.dateordo, a.nom, p.nom, e.nom, e.specialite
                ORDER BY o.dateordo DESC
                LIMIT %s OFFSET %s
                """
                cur.execute(query_ord, (nom_animal, f"%{nom_animal}%", nom_proprietaire, f"%{nom_proprietaire}%", items_per_page, (page_ord - 1) * items_per_page))
                ordonnances = cur.fetchall()

                cur.execute("SELECT COUNT(DISTINCT o.OrdoID) FROM Ordonnance o LEFT JOIN Animal a ON o.AnimalID = a.AnimalID LEFT JOIN Possede pos ON a.AnimalID = pos.AnimalID LEFT JOIN Proprietaire p ON pos.ProprietaireID = p.ProprietaireID WHERE (%s = '' OR a.nom ILIKE %s) AND (%s = '' OR p.nom ILIKE %s)", (nom_animal, f"%{nom_animal}%", nom_proprietaire, f"%{nom_proprietaire}%"))
                total_ordonnances = cur.fetchone()[0]
                total_pages_ord = (total_ordonnances + items_per_page - 1) // items_per_page

                # Requête pour les opérations
                query_op = """
                SELECT o.Date_operation, a.nom AS nom_animal, p.nom AS nom_proprietaire,
                       e.nom AS employe_nom, e.specialite, c.nom AS centre_nom, o.Nature_operation
                FROM Operation o
                LEFT JOIN Animal a ON o.AnimalID = a.AnimalID
                LEFT JOIN Possede pos ON a.AnimalID = pos.AnimalID
                LEFT JOIN Proprietaire p ON pos.ProprietaireID = p.ProprietaireID
                LEFT JOIN Employe e ON o.EmpID = e.EmpID
                LEFT JOIN Centre_veterinaire c ON o.CentreID = c.CentreID
                WHERE (%s = '' OR a.nom ILIKE %s) AND (%s = '' OR p.nom ILIKE %s)
                ORDER BY o.Date_operation DESC
                LIMIT %s OFFSET %s
                """
                cur.execute(query_op, (nom_animal, f"%{nom_animal}%", nom_proprietaire, f"%{nom_proprietaire}%", items_per_page, (page_op - 1) * items_per_page))
                operations = cur.fetchall()

                cur.execute("SELECT COUNT(DISTINCT o.OpeID) FROM Operation o LEFT JOIN Animal a ON o.AnimalID = a.AnimalID LEFT JOIN Possede pos ON a.AnimalID = pos.AnimalID LEFT JOIN Proprietaire p ON pos.ProprietaireID = p.ProprietaireID WHERE (%s = '' OR a.nom ILIKE %s) AND (%s = '' OR p.nom ILIKE %s)", (nom_animal, f"%{nom_animal}%", nom_proprietaire, f"%{nom_proprietaire}%"))
                total_operations = cur.fetchone()[0]
                total_pages_op = (total_operations + items_per_page - 1) // items_per_page

        return render_template(
            'historique_global.html',
            ordonnances=ordonnances,
            operations=operations,
            page_ord=page_ord,
            total_pages_ord=total_pages_ord,
            page_op=page_op,
            total_pages_op=total_pages_op,
            nom_animal=nom_animal,
            nom_proprietaire=nom_proprietaire
        )
    except Exception as e:
        flash(f"Erreur lors de la récupération de l'historique : {e}", "error")
        return redirect(url_for('espace_personnel'))












@app.route('/consulter_centres_employes', methods=['GET'])
def consulter_centres_employes():
    ville = request.args.get('ville', '').strip()
    page = int(request.args.get('page', 1))
    items_par_page = 5

    query = """
    SELECT c.nom AS centre_nom, c.adresse, c.telephone,
           COALESCE(e.nom || ' ' || e.prenom, 'Non renseigné') AS gerant_nom,
           STRING_AGG(DISTINCT em.nom || ' (' || em.specialite || ')', ', ') AS employes
    FROM Centre_veterinaire c
    LEFT JOIN Employe e ON c.EmpID = e.EmpID
    LEFT JOIN Travail t ON c.CentreID = t.CentreID
    LEFT JOIN Employe em ON t.EmpID = em.EmpID
    WHERE (%s = '' OR c.adresse ILIKE %s)
    GROUP BY c.CentreID, e.nom, e.prenom, c.adresse, c.telephone
    ORDER BY c.nom
    LIMIT %s OFFSET %s
    """
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (ville, f"%{ville}%", items_par_page, (page - 1) * items_par_page))
                centres = cur.fetchall()

        total_query = """
        SELECT COUNT(DISTINCT c.CentreID)
        FROM Centre_veterinaire c
        WHERE (%s = '' OR c.adresse ILIKE %s)
        """
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(total_query, (ville, f"%{ville}%"))
                total_items = cur.fetchone()[0]
        total_pages = (total_items + items_par_page - 1) // items_par_page

        return render_template(
            'consulter_centres_employes.html',
            centres=centres,
            page=page,
            total_pages=total_pages,
            ville=ville
        )
    except Exception as e:
        flash(f"Erreur lors de la récupération des centres et employés : {e}", "error")
        return redirect(url_for('espace_personnel'))




@app.route('/ajouter_vaccin', methods=['GET', 'POST'])
def ajouter_vaccin():
    if request.method == 'POST':
        nom = request.form['nom']
        type_vaccin = request.form['type']
        duree = int(request.form['duree'])
        animal_id = int(request.form['animal_id'])
        date = request.form['date']

        query = """
        INSERT INTO Vaccin (nom, type, duree, AnimalID, date)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (nom, type_vaccin, duree, animal_id, date))
                conn.commit()
            flash("Vaccin ajouté avec succès.", "success")
            return redirect(url_for('espace_personnel'))  # Redirection après ajout
        except Exception as e:
            flash(f"Erreur lors de l'ajout du vaccin : {e}", "error")
            return redirect(url_for('ajouter_vaccin'))

    # Récupérer la liste des animaux pour le menu déroulant
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT AnimalID, nom FROM Animal")
                animaux = cur.fetchall()
    except Exception as e:
        flash(f"Erreur lors de la récupération des animaux : {e}", "error")
        animaux = []

    return render_template('ajouter_vaccin.html', animaux=animaux)




if __name__ == '__main__':
    app.run(debug=True)
