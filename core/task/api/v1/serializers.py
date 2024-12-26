from rest_framework import serializers
from task.models import Task
from accounts.models import Profile
class TaskSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    class Meta:
        model = Task
        fields = ['title' ,'status' ,'author']



        """
        implementing with to representation
        """
    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     rep['author']=str(instance.author)
    #     return rep