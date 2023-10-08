from rest_framework import generics
from .models import Note
from .serializers import NoteSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import  urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated

# endpoint for create new note, POST--create note
class NoteListView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
#end point for edit/update,delete and retrieve note
#Put --edit,DELETE-delete,GET--retrieve/list note
class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated]
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

# register/create user endpoint
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')
        username=request.data.get('email')
        # Create a new user
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            username=username

        )

        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)

# login endpoint
@api_view(['POST'])
def login_user(request):
    
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        findUser=User.objects.get(email=email)
        if(findUser):
        # Authenticate user
            user = authenticate(username=email, password=password)

            if user is not None:
                login(request, user)
                return Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        else: 
            return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

# log out endpoint

@api_view(['POST'])
@login_required
def logout_user(request):
    if request.method == 'POST':
        # Log the user out
        logout(request)
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)

#update/reset password 
@api_view(['POST'])
def send_password_reset_email(request):
    if request.method == 'POST':
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            uid =user.pk
            

            reset_link = f'http://localhost:8000/reset_password/{uid}/'

            subject = 'Reset Your Password'
            message = f'Click the following link to reset your password: {reset_link}'

            send_mail(subject, message, 'your_email@example.com', [email])
            return Response({'message': 'Password reset email sent successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password(request, uidb64, token):
    if request.method == 'POST':
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                new_password = request.data.get('new_password')
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid reset link.'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)