from rest_framework import generics
from django.shortcuts import render
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
import tempfile
from reportlab.pdfgen import canvas
import csv
from django.http import HttpResponse
from django.db import IntegrityError
from django.template.loader import get_template
from xhtml2pdf import pisa
# endpoint for create new note, POST--create note
class NoteListView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        
        status = self.request.query_params.get('status')
        
             # sort according to latest date created
        if status == 'unfinished':
                return Note.objects.filter(status='unfinished')
        elif status == 'overdue':
            return Note.objects.filter(status='overdue')
        elif status == 'done':
            return Note.objects.filter(status='done')
         # sort according to latest date created
        else:
            sort_by = self.request.query_params.get('sort_by')
            queryset = Note.objects.all().order_by('-created_at')

            if sort_by == 'due_date':
                queryset = queryset.order_by('due_date')
            elif sort_by == 'priority':
                queryset = queryset.order_by('-priority')
            elif sort_by == 'created_at':
                queryset = queryset.order_by('-created_at')

            return queryset
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            return Response({'error': 'Note with same title or content already exists.'}, status=status.HTTP_400_BAD_REQUEST)    



#end point for edit/update,delete and retrieve note
#Put --edit,DELETE-delete,GET--retrieve/list note
class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated]
    queryset = Note.objects.all().order_by('-created_at')
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
         # Check if the user with the provided email already exists
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        # Create a new user
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            username=username

        )

        return Response({'message': 'User registered successfully.Use your email as your username when you want to login'}, status=status.HTTP_201_CREATED)

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
    
    
# export to pfd
     


# request='GET' 

def export_to_pdf(request):
    notes = Note.objects.all()
    context = {'notes': notes}
    template = get_template('pdf_templates/templates.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="notes.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))
    return response

# export_to_csv

# request='GET' 
def export_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="notes.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Content'])

    notes = Note.objects.all()
    for note in notes:
        
        writer.writerow([note.title, f'  {note.content}  '])

    return response
