import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from datetime import datetime 

URL = 'http://127.0.0.1:8000/api/v1/'
@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def get_user(client):
    response = client.post(f'{URL}auth/users/', data={'username': 'test10', 'password': 'kotleta44489'})
    response = client.post(f'{URL}token/', data ={'username': 'test10','password':'kotleta44489'})
    data = response.json()
    user_token = data['access']
    return user_token

@pytest.fixture
def create_news(client, get_user):
    headers = {'Authorization': f'Bearer {get_user}'}
    response = client.post(f'{URL}news/', data = {"title" : "test22", "description" : "test_description"}, headers=headers)
    created_news_id = response.json()
    return created_news_id['id']


@pytest.mark.django_db
def test_create_user_admin(client):
    #Arrange
    #Act
    response = client.post(f'{URL}auth/users/', data={'username': 'test1', 'password': 'kotleta44489'})
    data = response.json()
    User.objects.update(id=data['id'], is_staff = True)
    #Assert
    assert response.status_code == 201
    assert User.objects.get(id=data['id']).is_staff is True


@pytest.mark.django_db
def test_create_user_default(client):
    #Arrange
    #Act
    response = client.post(f'{URL}auth/users/', data={'username': 'test1', 'password': 'kotleta44489',})
    data = response.json()
    #Assert
    assert response.status_code == 201
    assert User.objects.get(id=data['id']).is_staff is False
    

@pytest.mark.django_db
def test_get_user_JWT_token(client):
    #Act
    response = client.post(f'{URL}auth/users/', data={'username': 'test1', 'password': 'kotleta44489'})
    response = client.post(f'{URL}token/', data ={'username': 'test1','password':'kotleta44489'})
    data = response.json()
    #Assert
    assert response.status_code == 200
    assert len(data['access']) > 20
    
@pytest.mark.django_db
def test_create_news(client, get_user):
    #Act
    headers = {'Authorization': f'Bearer {get_user}'}
    response = client.post(f'{URL}news/', data = {"title" : "test22", "description" : "test_description"}, headers=headers)
    data = response.json()
    #Assert
    assert response.status_code == 201
    assert data['title'] == "test22"

@pytest.mark.django_db
def test_delete_news_by_another_user(client, create_news):
    #Arrange (Создаем другово пользователя)
    response = client.post(f'{URL}auth/users/', data={'username': 'test2', 'password': 'kotleta44489',})
    response = client.post(f'{URL}token/', data ={'username': 'test2','password':'kotleta44489'})
    data_user = response.json()
    token_another_user = data_user['access']
    #Act (Пытаемся удалить чужую новость)
    news_id = create_news
    response = client.delete(f'{URL}news/{news_id}/', headers={'Authorization': f'Bearer {token_another_user}'})
    data = response.json()
    #Assert
    assert response.status_code == 403
    assert data['detail']== 'You do not have permission to perform this action.'
    
@pytest.mark.django_db
def test_delete_news_by_admin(client, create_news):
    #Arrange #create admin user and get JWT token
    User.objects.create_superuser(username='admin2', password='kotleta44489')
    response = client.post(f'{URL}token/', data ={'username': 'admin2','password':'kotleta44489'})
    item = response.json()
    admin_token= item['access']
    #Act
    response = client.delete(f'{URL}news/{create_news}/', headers={'Authorization': f'Bearer {admin_token}'})
    #Assert
    assert response.status_code == 204

@pytest.mark.django_db
def test_create_comment(client, create_news):
    #Arrange
    response = client.post(f'{URL}auth/users/', data={'username': 'test2', 'password': 'kotleta44489',})
    response = client.post(f'{URL}token/', data ={'username': 'test2','password':'kotleta44489'})
    data_user = response.json()
    #Act
    token_user = data_user['access']
    response = client.post(f'{URL}news/{create_news}/add_comment/', headers={'Authorization': f'Bearer {token_user}'}, data = {'description':'test_comment'})
    data = response.json()
    #Assert
    assert response.status_code == 200
    assert data['description'] == 'test_comment'

@pytest.mark.django_db
def test_delete_comment_from_post_author(client, create_news, get_user):
    #Arrange
    response = client.post(f'{URL}auth/users/', data={'username': 'test2', 'password': 'kotleta44489',})
    response = client.post(f'{URL}token/', data ={'username': 'test2','password':'kotleta44489'})
    data_user = response.json()
    token_user = data_user['access']
    response = client.post(f'{URL}news/{create_news}/add_comment/', headers={'Authorization': f'Bearer {token_user}'}, data = {'description':'test_comment'})
    data = response.json()
    #Act
    id_comment = data['id']
    response = client.delete(f'{URL}news/{create_news}/delete_comment/?comment_id={id_comment}' ,headers={'Authorization': f'Bearer {get_user}'},)
    data = response.json()
    #Assert
    assert data['status'] == 'ok'
    assert response.status_code == 200
    
@pytest.mark.django_db
def test_delete_comment_from_non_author(client, create_news):
    ### создаем новость и комент к ней
    response = client.post(f'{URL}auth/users/', data={'username': 'test2', 'password': 'kotleta44489',})
    response = client.post(f'{URL}token/', data ={'username': 'test2','password':'kotleta44489'})
    data_user = response.json()
    token_user = data_user['access']
    response = client.post(f'{URL}news/{create_news}/add_comment/', headers={'Authorization': f'Bearer {token_user}'}, data = {'description':'test_comment'})
    data = response.json()
    comment_id = data['id']
    ### создаем другово юзера
    response = client.post(f'{URL}auth/users/', data={'username': 'test11', 'password': 'kotleta44489'})
    response = client.post(f'{URL}token/', data ={'username': 'test11','password':'kotleta44489'})
    data = response.json()
    user_token = data['access']
    ### удаляем новость
    response = client.delete(f'{URL}news/{create_news}/delete_comment/?comment_id={comment_id}' ,headers={'Authorization': f'Bearer {user_token}'},)
    data = response.json()

    assert response.status_code == 200
    assert data['status'] == 'no_permissons'