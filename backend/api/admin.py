from django.contrib import admin
from .models import Role, Utilisateur, Departement, Filiere, Classe, Etudiant, Organisateur, Administrateur, TypeQuestion, Enquete, QuestionnaireEnquete, Question, ChoixReponse, CibleType, CibleEnquete, ParticipationEnquete, Reponse

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'matricule', 'role')  # Afficher ces champs dans la liste
    search_fields = ('username', 'last_name', 'matricule')  # Permettre la recherche par ces champs

admin.site.register(Role)
admin.site.register(Utilisateur,UtilisateurAdmin)
admin.site.register(Departement)
admin.site.register(Filiere)
admin.site.register(Classe)
admin.site.register(Etudiant)
admin.site.register(Organisateur)
admin.site.register(Administrateur)
admin.site.register(TypeQuestion)
admin.site.register(Enquete)
admin.site.register(QuestionnaireEnquete)
admin.site.register(Question)
admin.site.register(ChoixReponse)
admin.site.register(CibleType)
admin.site.register(CibleEnquete)
admin.site.register(ParticipationEnquete)
admin.site.register(Reponse)





