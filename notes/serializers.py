from rest_framework import serializers
from .models import Note

class NoteSerializer(serializers.ModelSerializer):
    is_complete = serializers.BooleanField(required=True)
    status = serializers.SerializerMethodField()
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at','due_date','is_complete','status']
    
    def get_status(self, obj):  #  method to get the status
        return obj.differentiate_status(obj.due_date)