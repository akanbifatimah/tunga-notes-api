from django.urls import path
from .views import NoteListView, NoteDetailView, register_user, login_user,logout_user,send_password_reset_email,reset_password,export_to_pdf,export_to_csv
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('notes/', NoteListView.as_view(), name='note-list'),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
    path('register/', register_user, name='register-user'),
    path('logout/', logout_user, name='logout-user'),
    path('password_reset_email/', send_password_reset_email, name='send-password-reset-email'),  
    path('reset_password/<uidb64>/<token>/', reset_password, name='reset-password'), 
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('export/pdf/', export_to_pdf, name='export-pdf'),
    path('export/csv/', export_to_csv, name='export-csv')
  
]
