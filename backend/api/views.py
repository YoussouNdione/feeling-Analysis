from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .utils import analyze_sentiment
from django.http import HttpResponse

from .models import (
    Role, Utilisateur, Departement, Filiere, Classe, Etudiant, Organisateur, 
    Administrateur, TypeQuestion, Enquete, QuestionnaireEnquete, Question, 
    ChoixReponse, CibleType, CibleEnquete, ParticipationEnquete, Reponse
)
from .serializers import (
    RoleSerializer, UtilisateurSerializer, DepartementSerializer, 
    FiliereSerializer, ClasseSerializer, EtudiantSerializer, 
    OrganisateurSerializer, AdministrateurSerializer, TypeQuestionSerializer, 
    EnqueteSerializer, QuestionnaireEnqueteSerializer, QuestionSerializer, 
    ChoixReponseSerializer, CibleTypeSerializer, CibleEnqueteSerializer, 
    ParticipationEnqueteSerializer, ReponseSerializer
)
from .permissions import IsAdminOrReadOnly, IsCreatorOrReadOnly, IsAdminOrOrganisateur


def home(request):
    return HttpResponse("Bienvenue sur l'API de Feeling Analysies dédié à l'établissement Unipro!")




class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['matricule', 'role__libelle']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'matricule']


class DepartementViewSet(viewsets.ModelViewSet):
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'libelle']


class FiliereViewSet(viewsets.ModelViewSet):
    queryset = Filiere.objects.all()
    serializer_class = FiliereSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['departement']
    search_fields = ['code', 'libelle']


class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['filiere', 'annee_academique']
    search_fields = ['code', 'libelle']


class EtudiantViewSet(viewsets.ModelViewSet):
    queryset = Etudiant.objects.all()
    serializer_class = EtudiantSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['classe', 'est_sorti', 'annee_obtention_diplome']
    search_fields = ['utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name', 'utilisateur__matricule']


class OrganisateurViewSet(viewsets.ModelViewSet):
    queryset = Organisateur.objects.all()
    serializer_class = OrganisateurSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ['utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name', 'utilisateur__matricule']


class AdministrateurViewSet(viewsets.ModelViewSet):
    queryset = Administrateur.objects.all()
    serializer_class = AdministrateurSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ['utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name', 'utilisateur__matricule']


class TypeQuestionViewSet(viewsets.ModelViewSet):
    queryset = TypeQuestion.objects.all()
    serializer_class = TypeQuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class EnqueteViewSet(viewsets.ModelViewSet):
    queryset = Enquete.objects.all()
    serializer_class = EnqueteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOrganisateur]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['est_active', 'createur']
    search_fields = ['titre', 'description']

    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'profil_etudiant'):
            etudiant = user.profil_etudiant
            departement_id = etudiant.classe.filiere.departement.id
            filiere_id = etudiant.classe.filiere.id
            classe_id = etudiant.classe.id
            
            return Enquete.objects.filter(
                est_active=True,
                date_debut__lte=timezone.now(),
                date_fin__gte=timezone.now(),
                cibles__in=CibleEnquete.objects.filter(
                    models.Q(departement_id=departement_id) |
                    models.Q(filiere_id=filiere_id) |
                    models.Q(classe_id=classe_id)
                )
            ).distinct()
        
        if hasattr(user, 'profil_administrateur'):
            return Enquete.objects.all()
        
        if hasattr(user, 'profil_organisateur'):
            return Enquete.objects.filter(createur=user)
        
        return Enquete.objects.none()
    
        return Response({"detail": "Enquête complétée avec succès."}, status=status.HTTP_201_CREATED)




    @action(detail=True, methods=['post'])
    def repondre(self, request, pk=None):
        enquete = self.get_object()
        etudiant = request.user.profil_etudiant
        
        if ParticipationEnquete.objects.filter(enquete=enquete, etudiant=etudiant).exists():
            return Response({"detail": "Vous avez déjà participé à cette enquête."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        participation = ParticipationEnquete.objects.create(
            enquete=enquete, 
            etudiant=etudiant,
            est_completee=True
        )
        
        reponses_data = request.data.get('reponses', [])
        for reponse_data in reponses_data:
            question_id = reponse_data.get('question_id')
            choix_id = reponse_data.get('choix_id')
            texte_libre = reponse_data.get('texte_libre')
            
            question = Question.objects.get(id=question_id)
            
            sentiment_score = None
            if texte_libre:
                sentiment_score = analyze_sentiment(texte_libre)
            
            Reponse.objects.create(
                question=question,
                etudiant=etudiant,
                choix_reponse_id=choix_id,
                texte_libre=texte_libre,
                sentiment_score=sentiment_score
            )
        
        return Response({"detail": "Enquête complétée avec succès."}, status=status.HTTP_201_CREATED)


   
    @action(detail=True, methods=['get'])
    def statistiques(self, request, pk=None):
        enquete = self.get_object()
        
        total_participants = ParticipationEnquete.objects.filter(enquete=enquete, est_completee=True).count()
        
        questions = Question.objects.filter(questionnaire__enquete=enquete)
        resultats = []
        
        for question in questions:
            stats = {
                'question_id': question.id,
                'question_texte': question.texte,
                'type': question.type.libelle,
                'total_reponses': Reponse.objects.filter(question=question).count(),
            }
            
            if question.type.libelle in ['QCM', 'Choix Unique']:
                choix_stats = []
                for choix in question.choix.all():
                    count = Reponse.objects.filter(question=question, choix_reponse=choix).count()
                    percentage = (count / stats['total_reponses'] * 100) if stats['total_reponses'] > 0 else 0
                    choix_stats.append({
                        'choix_id': choix.id,
                        'choix_texte': choix.texte,
                        'count': count,
                        'percentage': round(percentage, 2)
                    })
                stats['choix_stats'] = choix_stats
            
            if question.type.libelle in ['Texte Libre', 'Paragraphe']:
                sentiment_avg = Reponse.objects.filter(
                    question=question, 
                    sentiment_score__isnull=False
                ).aggregate(Avg('sentiment_score'))
                
                stats['sentiment_moyen'] = sentiment_avg['sentiment_score__avg']
                
                positif = Reponse.objects.filter(question=question, sentiment_score__gt=0.3).count()
                neutre = Reponse.objects.filter(question=question, sentiment_score__gte=-0.3, sentiment_score__lte=0.3).count()
                negatif = Reponse.objects.filter(question=question, sentiment_score__lt=-0.3).count()
                
                stats['sentiments'] = {
                    'positif': positif,
                    'neutre': neutre,
                    'negatif': negatif
                }
            
            resultats.append(stats)
        
        return Response({
            'total_participants': total_participants,
            'questions': resultats
        })


class QuestionnaireEnqueteViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireEnquete.objects.all()
    serializer_class = QuestionnaireEnqueteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOrganisateur]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['enquete']


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOrganisateur]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['questionnaire', 'type']


class ChoixReponseViewSet(viewsets.ModelViewSet):
    queryset = ChoixReponse.objects.all()
    serializer_class = ChoixReponseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOrganisateur]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question']


class CibleTypeViewSet(viewsets.ModelViewSet):
    queryset = CibleType.objects.all()
    serializer_class = CibleTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class CibleEnqueteViewSet(viewsets.ModelViewSet):
    queryset = CibleEnquete.objects.all()
    serializer_class = CibleEnqueteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOrganisateur]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['enquete', 'type', 'departement', 'filiere', 'classe']


class ParticipationEnqueteViewSet(viewsets.ModelViewSet):
    queryset = ParticipationEnquete.objects.all()
    serializer_class = ParticipationEnqueteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['enquete', 'etudiant', 'est_completee']

    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'profil_etudiant'):
            return ParticipationEnquete.objects.filter(etudiant=user.profil_etudiant)
        
        if hasattr(user, 'profil_administrateur'):
            return ParticipationEnquete.objects.all()
        
        if hasattr(user, 'profil_organisateur'):
            return ParticipationEnquete.objects.filter(enquete__createur=user)
        
        return ParticipationEnquete.objects.none()


class ReponseViewSet(viewsets.ModelViewSet):
    queryset = Reponse.objects.all()
    serializer_class = ReponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question', 'etudiant']

    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'profil_etudiant'):
            return Reponse.objects.filter(etudiant=user.profil_etudiant)
        
        if hasattr(user, 'profil_administrateur'):
            return Reponse.objects.all()
        
        if hasattr(user, 'profil_organisateur'):
            return Reponse.objects.filter(question__questionnaire__enquete__createur=user)
        
        return Reponse.objects.none()
    
    @action(detail=False, methods=['get'])
    def analyse_sentiments(self, request):
        """Endpoint pour l'analyse globale des sentiments"""
        enquete_id = request.query_params.get('enquete_id')
        
        reponses = self.get_queryset().filter(sentiment_score__isnull=False)
        
        if enquete_id:
            reponses = reponses.filter(question__questionnaire__enquete_id=enquete_id)
        
        results = []
        for question in Question.objects.filter(reponses__in=reponses).distinct():
            question_reponses = reponses.filter(question=question)
            sentiment_avg = question_reponses.aggregate(Avg('sentiment_score'))['sentiment_score__avg']
            
            positif = question_reponses.filter(sentiment_score__gt=0.3).count()
            neutre = question_reponses.filter(sentiment_score__gte=-0.3, sentiment_score__lte=0.3).count()
            negatif = question_reponses.filter(sentiment_score__lt=-0.3).count()
            
            results.append({
                'question_id': question.id,
                'question_texte': question.texte,
                'sentiment_moyen': sentiment_avg,
                'total_reponses': question_reponses.count(),
                'sentiments': {
                    'positif': positif,
                    'neutre': neutre,
                    'negatif': negatif
                }
            })
        
        return Response(results)