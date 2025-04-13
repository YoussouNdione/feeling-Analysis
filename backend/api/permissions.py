from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée qui autorise les administrateurs à effectuer
    toutes les opérations, mais permet seulement les opérations de lecture
    aux autres utilisateurs.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return request.user and hasattr(request.user, 'profil_administrateur')


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée qui autorise les créateurs d'un objet à le modifier,
    mais permet seulement les opérations de lecture aux autres utilisateurs.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.createur == request.user


class IsAdminOrOrganisateur(permissions.BasePermission):
    """
    Permission personnalisée qui autorise les administrateurs et les organisateurs
    à effectuer toutes les opérations, mais limite les autres utilisateurs.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (hasattr(request.user, 'profil_administrateur') or 
                hasattr(request.user, 'profil_organisateur'))
    
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'profil_administrateur'):
            return True
        
        if hasattr(request.user, 'profil_organisateur'):
            if hasattr(obj, 'createur'):
                return obj.createur == request.user
            
            if hasattr(obj, 'enquete'):
                return obj.enquete.createur == request.user
        
        return False