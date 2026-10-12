-- Création des tables

CREATE TABLE Proprietaire (
    ProprietaireID SERIAL PRIMARY KEY,
    Nom VARCHAR(100) NOT NULL,
    Prenom VARCHAR(100) NOT NULL,
    Adresse VARCHAR(100) NOT NULL,
    Telephone VARCHAR(20) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Animal (
    AnimalID SERIAL PRIMARY KEY,
    espece VARCHAR(50) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 0) NOT NULL,
    sexe CHAR(1) NOT NULL,
    signe_distinct TEXT,
    date_inscrit DATE NOT NULL
);

CREATE TABLE Possede (
    ProprietaireID INT REFERENCES Proprietaire(ProprietaireID) ON DELETE CASCADE ON UPDATE CASCADE,
    AnimalID INT REFERENCES Animal(AnimalID) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (ProprietaireID, AnimalID)
);

CREATE TABLE Vaccin (
    IdVaccin SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    duree INT NOT NULL,
    AnimalID INT REFERENCES Animal(AnimalID) ON DELETE CASCADE ON UPDATE CASCADE,
    date DATE NOT NULL
);

CREATE TABLE Medicament (
    MedocID SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Employe (
    EmpID SERIAL PRIMARY KEY,
    specialite VARCHAR(100) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    Adresse VARCHAR(100) NOT NULL,
    Telephone VARCHAR(20) NOT NULL,
    DateNaissance DATE NOT NULL,
    Numsecu VARCHAR(20) UNIQUE NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    date_embauche DATE NOT NULL,
    mot_de_passe VARCHAR(100) NOT NULL
);

CREATE TABLE Ordonnance (
    OrdoID SERIAL PRIMARY KEY,
    dateordo DATE NOT NULL,
    AnimalID INT REFERENCES Animal(AnimalID) ON DELETE CASCADE ON UPDATE CASCADE,
    EmpID INT REFERENCES Employe(EmpID) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE Contient (
    OrdoID INT REFERENCES Ordonnance(OrdoID) ON DELETE CASCADE ON UPDATE CASCADE,
    MedocID INT REFERENCES Medicament(MedocID) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (OrdoID, MedocID)
);

CREATE TABLE Centre_veterinaire (
    CentreID SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    adresse VARCHAR(100) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    EmpID INT UNIQUE REFERENCES Employe(EmpID) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE Travail (
    EmpID INT REFERENCES Employe(EmpID) ON DELETE CASCADE ON UPDATE CASCADE,
    CentreID INT REFERENCES Centre_veterinaire(CentreID) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (EmpID, CentreID)
);

CREATE TABLE Est_dans (
    AnimalID INT REFERENCES Animal(AnimalID) ON DELETE CASCADE ON UPDATE CASCADE,
    CentreID INT REFERENCES Centre_veterinaire(CentreID) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (AnimalID, CentreID)
);

CREATE TABLE Operation (
    OpeID SERIAL PRIMARY KEY,
    Date_operation DATE NOT NULL,
    Nature_operation VARCHAR(100) NOT NULL,
    EmpID INT REFERENCES Employe(EmpID) ON DELETE SET NULL ON UPDATE CASCADE,
    AnimalID INT REFERENCES Animal(AnimalID) ON DELETE CASCADE ON UPDATE CASCADE,
    CentreID INT REFERENCES Centre_veterinaire(CentreID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Insertion des données après la création de toutes les tables

ALTER TABLE Centre_veterinaire ADD CONSTRAINT unique_directeur UNIQUE (EmpID);


ALTER TABLE Ordonnance
ADD CONSTRAINT check_dateordo_valid CHECK (dateordo <= CURRENT_DATE);


ALTER TABLE Operation
ADD CONSTRAINT check_date_operation
CHECK (Date_operation <= CURRENT_DATE);


-- Contraintes pour éviter des âges négatifs
ALTER TABLE Animal
ADD CONSTRAINT check_age_positive CHECK (age >= 0);


ALTER TABLE Proprietaire
ADD CONSTRAINT check_telephone_length CHECK (LENGTH(Telephone) = 10);






-- Insertion de 6 propriétaires
INSERT INTO Proprietaire (Nom, Prenom, Adresse, Telephone, Email) VALUES 
('Dupont', 'Marie', '10 Rue de Paris', '0612345678', 'marie.dupont@gmail.com'),
('Bert', 'Theo', '12 Rue de Lyon', '0623456789', 'theo.bert@gmail.com'),
('Donta', 'Julie', '14 Rue de Lille', '0634567890', 'julie.donta@gmail.com'),
('Martin', 'Paul', '16 Rue de Marseille', '0645678901', 'paul.martin@gmail.com'),
('Petit', 'Laura', '18 Rue de Bordeaux', '0656789012', 'laura.petit@gmail.com'),
('Roux', 'Hugo', '20 Rue de Strasbourg', '0667890123', 'hugo.roux@gmail.com');

-- Insertion de 6 animaux
INSERT INTO Animal (espece, nom, age, sexe, signe_distinct, date_inscrit) VALUES 
('Chien', 'Rex', 5, 'M', 'Pelage noir', '2023-01-15'),
('Lapin', 'Coco', 2, 'F', 'Oreilles longues', '2023-02-20'),
('Chat', 'Garfield', 3, 'M', 'Poil roux', '2023-03-25'),
('Furet', 'Zelda', 1, 'F', NULL, '2023-04-15'),
('Chien', 'Max', 4, 'M', 'Collier rouge', '2023-05-05'),
('Lapin', 'Lily', 2, 'F', NULL, '2023-06-10');

-- Liaison des animaux avec leurs propriétaires
INSERT INTO Possede (ProprietaireID, AnimalID) VALUES 
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6);

-- Insertion de 6 vaccins
INSERT INTO Vaccin (nom, type, duree, AnimalID, date) VALUES 
('Rage', 'Virus', 12, 1, '2023-01-01'),
('Leptospirose', 'Bactérie', 12, 2, '2023-02-01'),
('Tétanos', 'Bactérie', 24, 3, '2023-03-01'),
('Hépatite', 'Virus', 12, 4, '2023-04-01'),
('Parvovirose', 'Virus', 36, 5, '2023-05-01'),
('Coryza', 'Virus', 12, 6, '2023-06-01');

-- Insertion de 6 médicaments
INSERT INTO Medicament (nom) VALUES 
('Antibiotique'), ('Anti-inflammatoire'), ('Vermifuge'),
('Antiviral'), ('Antiparasitaire'), ('Antihistaminique');

-- Insertion de 6 employés
INSERT INTO Employe (specialite, nom, prenom, Adresse, Telephone, DateNaissance, Numsecu, login, date_embauche, mot_de_passe) VALUES 
('Chirurgie', 'Jean', 'Alice', '10 Rue de Paris', '0612345678', '1980-05-15', '1234567890123', 'jean_a', '2015-07-01', 'password1'),
('Dentisterie', 'Martin', 'Alice', '12 Rue de Lyon', '0623456789', '1985-03-20', '2345678901234', 'martin_a', '2020-06-01', 'password2'),
('Cardiologie', 'Dupont', 'Jean', '14 Rue de Marseille', '0634567890', '1978-11-05', '3456789012345', 'dupont_j', '2019-05-15', 'password3'),
('Dermatologie', 'Durand', 'Clara', '16 Rue de Lille', '0645678901', '1990-07-12', '4567890123456', 'durand_c', '2021-09-10', 'password4'),
('Neurologie', 'Garcia', 'Julien', '18 Rue de Rennes', '0656789012', '1982-08-15', '5678901234567', 'garcia_j', '2021-01-15', 'password5'),
('Pédiatrie', 'Petit', 'Laura', '20 Rue de Bordeaux', '0667890123', '1990-03-10', '6789012345678', 'petit_l', '2020-03-10', 'password6');

-- Insertion de 6 centres vétérinaires
INSERT INTO Centre_veterinaire (nom, adresse, telephone, EmpID) VALUES 
('Clinique Paris', '10 Rue de Paris', '0612345678', 1),
('Centre Lyon', '12 Rue de Lyon', '0623456789', 2),
('Clinique Marseille', '14 Rue de Marseille', '0634567890', 3),
('Centre Lille', '16 Rue de Lille', '0645678901', 4),
('Clinique Rennes', '18 Rue de Rennes', '0656789012', 5),
('Centre Bordeaux', '20 Rue de Bordeaux', '0667890123', 6);

-- Association des employés aux centres (employés supplémentaires travaillant dans chaque centre)
INSERT INTO Travail (EmpID, CentreID) VALUES 
(1, 1), (2, 1), (3, 2), (4, 3), (5, 3), (6, 4);

-- Insertion d'ordonnances
INSERT INTO Ordonnance (dateordo, AnimalID, EmpID) VALUES 
('2024-01-10', 1, 1),
('2024-02-15', 2, 2),
('2024-03-20', 3, 3),
('2024-04-25', 4, 4),
('2024-05-05', 5, 5),
('2024-06-10', 6, 6);

-- Liaison des médicaments aux ordonnances
INSERT INTO Contient (OrdoID, MedocID) VALUES 
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6);

-- Insertion de 6 opérations
INSERT INTO Operation (Date_operation, Nature_operation, EmpID, AnimalID, CentreID) VALUES 
('2024-01-01', 'Stérilisation', 1, 1, 1),
('2024-02-01', 'Chirurgie', 2, 2, 2),
('2024-03-01', 'Vaccination', 3, 3, 3),
('2024-04-01', 'Extraction dentaire', 4, 4, 4),
('2024-05-01', 'Chirurgie', 5, 5, 5),
('2024-06-01', 'Radiographie', 6, 6, 6);




-- login personnel
SELECT login, mot_de_passe
FROM Employe;

-- login particulier 
SELECT p.Nom AS Nom_Proprietaire, a.AnimalID, a.nom AS Nom_Animal
FROM Proprietaire p
JOIN Possede pos ON p.ProprietaireID = pos.ProprietaireID
JOIN Animal a ON pos.AnimalID = a.AnimalID;


--supprimmer toutes les tables

DO $$
DECLARE
    table_name TEXT;
BEGIN
    FOR table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(table_name) || ' CASCADE';
    END LOOP;
END $$;







