from rest_framework import serializers
from news.models import News, Comments, UserNewRelation
from rest_framework.fields import SerializerMethodField
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class CommentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comments
        fields = ('id','description', 'autor', 'created_at',)
        
class UserNewsSerializer(serializers.ModelSerializer):
    liked_by_users = SerializerMethodField()
    
    class Meta:
        model = UserNewRelation
        fields = ('liked_by_users',)
    
    def get_liked_by_users(self, instance):
        return instance.id
    

class NewsSerializer(serializers.ModelSerializer):
    comments = CommentsSerializer(many=True, read_only=True,)
    like = UserNewsSerializer(many=True, read_only=True)
    total_likes = SerializerMethodField()
    autor = UserSerializer(
        read_only=True,
    )
    
    class Meta:
        model = News
        fields= ('id','title','description', 'autor', 'created_at', 'comments', 'like', 'total_likes',)
        
    def create(self, validated_data):
        
        validated_data["autor"] = self.context["request"].user
        return super().create(validated_data)
        
    
    
    def get_total_likes(self, instance):
        return instance.like.count()
    