from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from news.fiters import NewsFilter
from news.models import News, Comments
from rest_framework.filters import SearchFilter
from news.permissions import IsOwner_or_Admin
from news.serializers import CommentsSerializer, NewsSerializer, UserNewsSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

class NewsViewSet(ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filterset_class = NewsFilter
    filter_backends = [SearchFilter]
    search_fields = ['title', 'description']
    
    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", 'destroy',]:
            return [IsOwner_or_Admin(), IsAuthenticated(),]
        return []

    def get_queryset(self, *args, **kwargs):
        """Черновики видят только админы и создатели"""
        if self.request.user.is_staff:
            return News.objects.all()
        if self.request.user.is_anonymous:
            return News.objects.exclude(status='DRAFT')
        return News.objects.filter(Q(autor=self.request.user) | ~Q(status='DRAFT'))


    @action(detail=True,url_path='add_comment', methods=['POST'], permission_classes=[IsAuthenticated(), ])
    def create_comment(self, request, pk):
        """Создаем коммент к новости"""
        queryset = News.objects.get(id = pk)
        if queryset:
            validated_data = {'post' :queryset, 'autor':request.user, 'description':request.data['description']}
            serializer = CommentsSerializer(data=validated_data)
            data = serializer.create(validated_data)
            return Response ({'description':data.description, 'id':data.id})
    
        
    @action(detail=True,url_path='delete_comment', methods=['DELETE'], permission_classes=[IsAuthenticated(), IsOwner_or_Admin() ])
    def delete_coment(self, request, pk):
        """Удаляем коммент, удалить может либо автор новости, либо создатель комента или админ"""
        queryset = News.objects.get(id = pk)
        if request.user == Comments.objects.get(post=queryset, id=request.query_params.get('comment_id')).autor or request.user.is_staff or request.user == queryset.autor:
            Comments.objects.get(post=queryset, id=request.query_params.get('comment_id')).delete()
            return Response ({'status':'ok'})
        else: return Response({'status':'no_permissons'})
    
    
    @action(detail=True,url_path='update_comment', methods=['PATCH'])
    def update_comment(self, request, pk):
        queryset = News.objects.get(id=pk)
        if request.user == Comments.objects.get(post=queryset,id = 11).autor or request.user.is_staff:
            Comments.objects.update(post=queryset, id=4, description = request.data['description'])
            return Response ({'status':'ok'})
        else: return Response('no permissons')
    
    
    @action(detail=True,url_path='like_toggle', methods=['POST'], permission_classes=[IsAuthenticated(), ])
    def toggle_like(self,request, *args, **kwargs):
        """лайкаем новость, toggle"""
        obj= self.get_object()
        if obj.like.filter(id=request.user.id):
            obj.like.remove(request.user)
            return Response('Лайк убран')
        else:
            obj.like.add(request.user)
            return Response('Лайк поставлен')
    
    
    @action(detail=False,url_path='my_liked_news', methods=['GET'], permission_classes=[IsAuthenticated(), ])
    def my_liked_news(self, request, *args, **kwargs):
        """получить список новостей которые лайкнул текущий юзер"""
        queryset = News.objects.filter(like=self.request.user.id)
        serializer = NewsSerializer(queryset,many=True)
        return Response(serializer.data)
    
    
    @action(detail=False,url_path='likes_order', methods=['GET'],)
    def order_likes(self, *args, **kwargs):
        """отсортировать по количеству лайков"""
        queryset = super().get_queryset()
        serializer = NewsSerializer(queryset, many=True)
        return Response(sorted((serializer.data), key=lambda item:item["total_likes"], reverse=True))
