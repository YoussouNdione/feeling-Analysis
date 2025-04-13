from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class Role(models.Model):
    """Rôles des utilisateurs"""
    libelle = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.libelle


class Utilisateur(AbstractUser):
    """Extension du modèle utilisateur de Django"""
    matricule = models.CharField(max_length=20, unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True)

    class Meta:
        db_table = 'utilisateur'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.matricule})"


class Departement(models.Model):
    """Département académique"""
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.libelle


class Filiere(models.Model):
    """Filière académique"""
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='filieres')

    def __str__(self):
        return self.libelle


class Classe(models.Model):
    """Classe académique"""
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=100)
    annee_academique = models.CharField(max_length=9)  # Format: 2023-2024
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='classes')

    def __str__(self):
        return f"{self.libelle} ({self.annee_academique})"


class Etudiant(models.Model):
    """Profil spécifique pour les étudiants"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, primary_key=True, related_name='profil_etudiant')
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name='etudiants')
    annee_obtention_diplome = models.IntegerField(null=True, blank=True)
    est_sorti = models.BooleanField(default=False)

    def __str__(self):
        return str(self.utilisateur)


class Organisateur(models.Model):
    """Profil spécifique pour les organisateurs"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, primary_key=True, related_name='profil_organisateur')

    def __str__(self):
        return str(self.utilisateur)


class Administrateur(models.Model):
    """Profil spécifique pour les administrateurs"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, primary_key=True, related_name='profil_administrateur')

    def __str__(self):
        return str(self.utilisateur)


class TypeQuestion(models.Model):
    """Types de questions (QCM, Texte libre, etc.)"""
    libelle = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.libelle


class Enquete(models.Model):
    """Enquête créée par un organisateur ou administrateur"""
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    est_active = models.BooleanField(default=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='enquetes_creees')

    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = 'Enquête'
        verbose_name_plural = 'Enquêtes'


class QuestionnaireEnquete(models.Model):
    """Section de questionnaire dans une enquête"""
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name='questionnaires')
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.titre} - {self.enquete.titre}"
    
    class Meta:
        verbose_name = 'Questionnaire'
        verbose_name_plural = 'Questionnaires'


class Question(models.Model):
    """Question dans un questionnaire"""
    questionnaire = models.ForeignKey(QuestionnaireEnquete, on_delete=models.CASCADE, related_name='questions')
    texte = models.TextField()
    type = models.ForeignKey(TypeQuestion, on_delete=models.PROTECT)
    est_obligatoire = models.BooleanField(default=True)
    ordre = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['ordre']
    
    def __str__(self):
        return self.texte[:50]


class ChoixReponse(models.Model):
    """Choix possibles pour les questions à choix multiples"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix')
    texte = models.CharField(max_length=255)
    ordre = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['ordre']
    
    def __str__(self):
        return self.texte


class CibleType(models.Model):
    """Types de cibles pour les enquêtes (département, filière, classe)"""
    libelle = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.libelle


class CibleEnquete(models.Model):
    """Définit à qui est destinée l'enquête"""
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name='cibles')
    type = models.ForeignKey(CibleType, on_delete=models.PROTECT)
    # Ces champs peuvent être null selon le type de cible
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, null=True, blank=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, null=True, blank=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        if self.departement:
            return f"Enquête '{self.enquete.titre}' - Département: {self.departement.libelle}"
        elif self.filiere:
            return f"Enquête '{self.enquete.titre}' - Filière: {self.filiere.libelle}"
        elif self.classe:
            return f"Enquête '{self.enquete.titre}' - Classe: {self.classe.libelle}"
        return f"Enquête '{self.enquete.titre}' - Cible non spécifiée"


class ParticipationEnquete(models.Model):
    """Trace la participation d'un étudiant à une enquête"""
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name='participations')
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='participations')
    date_participation = models.DateTimeField(auto_now_add=True)
    est_completee = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['enquete', 'etudiant']
        verbose_name = 'Participation'
        verbose_name_plural = 'Participations'
    
    def __str__(self):
        return f"{self.etudiant} - {self.enquete.titre}"


class Reponse(models.Model):
    """Réponses des étudiants aux questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reponses')
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='reponses')
    choix_reponse = models.ForeignKey(ChoixReponse, on_delete=models.SET_NULL, null=True, blank=True, related_name='reponses')
    texte_libre = models.TextField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    date_reponse = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['question', 'etudiant']
    
    def __str__(self):
        return f"Réponse de {self.etudiant} à {self.question}"