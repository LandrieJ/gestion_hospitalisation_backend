from django.urls import path
from .views import (
    UserView,
    UserDetailView,
    LoginView,
    LogoutView,
    SessionView,
    get_csrf_token,
    PasswordResetView,
    EducationView,
    EducationDetailView,
    CompetenceView,
    CompetenceDetailView,
    HorairesView,
)

urlpatterns = [
    ## User View urlpattern
    path("users/", UserView.as_view(), name="user_list"),
    path("users/<int:user_id>/", UserDetailView.as_view(), name="user_detail"),
    
    ## User Education View urlpattern
    path("users/<int:user_id>/education/", EducationView.as_view(), name="user_education"),
    path("users/<int:user_id>/education/<int:education_id>/", EducationDetailView.as_view(), name="user_education_detail"),
    
    ## User Experience View urlpattern
    path("users/<int:user_id>/competence/", CompetenceView.as_view(), name="user_competence"),
    path("users/<int:user_id>/competence/<int:competence_id>/", CompetenceDetailView.as_view(), name="user_competence_detail"),
    
    ## User Horaire View urlpattern
    path("users/<int:user_id>/horaires/", HorairesView.as_view(), name="user_horaires_travail"),
    
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("session/", SessionView.as_view(), name="session"),
    path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),
]

