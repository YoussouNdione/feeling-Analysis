from rest_framework import serializers
from .models import (
    Role, Utilisateur, Departement, Filiere, Classe, Etudiant, Organisateur, 
    Administrateur, TypeQuestion, Enquete, QuestionnaireEnquete, Question, 
    ChoixReponse, CibleType, CibleEnquete, ParticipationEnquete, Reponse
)
from django.contrib.auth.password_validation import validate_password


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UtilisateurSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Utilisateur
        fields = ('id', 'username', 'password', 'confirm_password', 'matricule', 'email', 
                  'first_name', 'last_name', 'role')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs
    
    def create(self, validated_data):
        user = Utilisateur.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            matricule=validated_data['matricule'],
            role=validated_data.get('role')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class DepartementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = '__all__'


class FiliereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filiere
        fields = '__all__'


class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = '__all__'


class EtudiantSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(required=True)
    
    class Meta:
        model = Etudiant
        fields = '__all__'
    
    def create(self, validated_data):
        utilisateur_data = validated_data.pop('utilisateur')
        utilisateur_serializer = UtilisateurSerializer(data=utilisateur_data)
        utilisateur_serializer.is_valid(raise_exception=True)
        utilisateur = utilisateur_serializer.save()
        
        role_etudiant, _ = Role.objects.get_or_create(libelle='Étudiant')
        utilisateur.role = role_etudiant
        utilisateur.save()
        
        etudiant = Etudiant.objects.create(utilisateur=utilisateur, **validated_data)
        return etudiant


class OrganisateurSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(required=True)
    
    class Meta:
        model = Organisateur
        fields = '__all__'
    
    def create(self, validated_data):
        utilisateur_data = validated_data.pop('utilisateur')
        utilisateur_serializer = UtilisateurSerializer(data=utilisateur_data)
        utilisateur_serializer.is_valid(raise_exception=True)
        utilisateur = utilisateur_serializer.save()
        
        role_organisateur, _ = Role.objects.get_or_create(libelle='Organisateur')
        utilisateur.role = role_organisateur
        utilisateur.save()
        
        organisateur = Organisateur.objects.create(utilisateur=utilisateur)
        return organisateur


class AdministrateurSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(required=True)
    
    class Meta:
        model = Administrateur
        fields = '__all__'
    
    def create(self, validated_data):
        utilisateur_data = validated_data.pop('utilisateur')
        utilisateur_serializer = UtilisateurSerializer(data=utilisateur_data)
        utilisateur_serializer.is_valid(raise_exception=True)
        utilisateur = utilisateur_serializer.save()
        
        role_admin, _ = Role.objects.get_or_create(libelle='Administrateur')
        utilisateur.role = role_admin
        utilisateur.save()
        
        admin = Administrateur.objects.create(utilisateur=utilisateur)
        return admin


class TypeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeQuestion
        fields = '__all__'


class ChoixReponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoixReponse
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    choix = ChoixReponseSerializer(many=True, required=False)
    
    class Meta:
        model = Question
        fields = '__all__'
    
    def create(self, validated_data):
        choix_data = validated_data.pop('choix', [])
        question = Question.objects.create(**validated_data)
        
        for choix in choix_data:
            ChoixReponse.objects.create(question=question, **choix)
        
        return question

class QuestionnaireEnqueteSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    
    class Meta:
        model = QuestionnaireEnquete
        fields = '__all__'
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        questionnaire = QuestionnaireEnquete.objects.create(**validated_data)
        
        for ordre, question_data in enumerate(questions_data, 1):
            choix_data = question_data.pop('choix', [])
            question_data['ordre'] = ordre
            question = Question.objects.create(questionnaire=questionnaire, **question_data)
            
            for o, choix in enumerate(choix_data, 1):
                choix['ordre'] = o
                ChoixReponse.objects.create(question=question, **choix)
        
        return questionnaire


class CibleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CibleType
        fields = '__all__'


class CibleEnqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CibleEnquete
        fields = '__all__'


class EnqueteSerializer(serializers.ModelSerializer):
    questionnaires = QuestionnaireEnqueteSerializer(many=True, required=False)
    cibles = CibleEnqueteSerializer(many=True, required=False)
    
    class Meta:
        model = Enquete
        fields = '__all__'
    
    def create(self, validated_data):
        questionnaires_data = validated_data.pop('questionnaires', [])
        cibles_data = validated_data.pop('cibles', [])
        
        enquete = Enquete.objects.create(**validated_data)
        
        for questionnaire_data in questionnaires_data:
            questions_data = questionnaire_data.pop('questions', [])
            questionnaire = QuestionnaireEnquete.objects.create(enquete=enquete, **questionnaire_data)
            
            for ordre, question_data in enumerate(questions_data, 1):
                choix_data = question_data.pop('choix', [])
                question_data['ordre'] = ordre
                question = Question.objects.create(questionnaire=questionnaire, **question_data)
                
                for o, choix in enumerate(choix_data, 1):
                    choix['ordre'] = o
                    ChoixReponse.objects.create(question=question, **choix)
        
        for cible_data in cibles_data:
            CibleEnquete.objects.create(enquete=enquete, **cible_data)
        
        return enquete


class ParticipationEnqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipationEnquete
        fields = '__all__'


class ReponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reponse
        fields = '__all__'