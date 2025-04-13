from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'utilisateurs', views.UtilisateurViewSet)
router.register(r'departements', views.DepartementViewSet)
router.register(r'filieres', views.FiliereViewSet)
router.register(r'classes', views.ClasseViewSet)
router.register(r'etudiants', views.EtudiantViewSet)
router.register(r'organisateurs', views.OrganisateurViewSet)
router.register(r'administrateurs', views.AdministrateurViewSet)
router.register(r'types-questions', views.TypeQuestionViewSet)
router.register(r'enquetes', views.EnqueteViewSet)
router.register(r'questionnaires', views.QuestionnaireEnqueteViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'choix-reponses', views.ChoixReponseViewSet)
router.register(r'cibles-types', views.CibleTypeViewSet)
router.register(r'cibles-enquetes', views.CibleEnqueteViewSet)
router.register(r'participations', views.ParticipationEnqueteViewSet)
router.register(r'reponses', views.ReponseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    
]


