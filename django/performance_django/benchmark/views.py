import base64
import json

from django.http import JsonResponse
from django.utils import connection
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import make_password, check_password
from .models import User, FileModel, Product, Order, OrderProduct
from .serializers import UserSerializer, FileModelSerializer
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.db import connection


def get_users(request):
    users = list(User.objects.values('id', 'name', 'email', 'age'))
    return JsonResponse(users, safe=False)


def get_user(request, user_id):
    try:
        user = User.objects.values('id', 'name', 'email', 'age').get(id=user_id)
        return JsonResponse(user)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)


@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = User.objects.create(
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            age=data.get('age')
        )
        return JsonResponse({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'age': user.age
        }, status=201)
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def update_user(request, user_id):
    if request.method == 'PUT':
        try:
            user = User.objects.get(id=user_id)
            data = json.loads(request.body)

            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            user.age = data.get('age', user.age)
            user.save()

            return JsonResponse({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'age': user.age
            })
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({}, status=204)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def users_list(request):
    if request.method == 'GET':
        return get_users(request)
    elif request.method == 'POST':
        return create_user(request)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def user_detail(request, user_id):
    if request.method == 'GET':
        return get_user(request, user_id)
    elif request.method == 'PUT':
        return update_user(request, user_id)
    elif request.method == 'DELETE':
        return delete_user(request, user_id)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        data = request.data
        try:
            user = User.objects.create(
                name=data['name'],
                email=data['email'],
                password=make_password(data['password']),
            )
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        data = request.data
        try:
            user = User.objects.get(email=data['email'])
            if check_password(data['password'], user.password):
                token = generate_jwt_token(user)
                return Response({"token": token}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


def generate_jwt_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


@api_view(['POST'])
def upload_file(request):
    if request.method == 'POST':
        serializer = FileModelSerializer(data=request.data)

        if serializer.is_valid():
            file_instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_file(request, file_id):
    try:
        file_instance = FileModel.objects.get(id=file_id)
    except FileModel.DoesNotExist:
        return Response({"message": "File not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = FileModelSerializer(file_instance)

    file_data = file_instance.file_data

    response = JsonResponse({
        'name': file_instance.name,
        'fileData': base64.b64encode(file_data).decode('utf-8')
    })

    return response


@api_view(['GET'])
def get_products(request):
    limit = int(request.GET.get('limit', 10))
    offset = int(request.GET.get('offset', 0))
    direction = request.GET.get('direction', 'ASC').upper()

    if direction not in ['ASC', 'DESC']:
        return JsonResponse({'error': 'Invalid direction value'}, status=400)

    try:
        products = Product.objects.all()

        if direction == 'DESC':
            products = products.order_by('-price')
        else:
            products = products.order_by('price')

        products = products[offset:offset + limit]

        results = list(products.values('id', 'name', 'price', 'stock'))

        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Error retrieving products', 'details': str(e)}, status=500)


@api_view(['GET'])
def get_popular_products(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.price,
                    COALESCE(SUM(op.quantity), 0) as total_quantity
                FROM 
                    products p
                LEFT JOIN 
                    order_products op ON p.id = op.product_id
                GROUP BY 
                    p.id, p.name, p.price
                ORDER BY 
                    total_quantity DESC
                LIMIT 10
            """)

            rows = cursor.fetchall()
            results = [
                {
                    'id': row[0],
                    'name': row[1],
                    'price': row[2],
                    'total_quantity': row[3]
                } for row in rows
            ]
            return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Error fetching popular products', 'details': str(e)}, status=500)


@api_view(['GET'])
def get_orders(request):
    try:
        user_id = int(request.GET.get('userId', 0))
        start_date = request.GET.get('startDate', '')
        end_date = request.GET.get('endDate', '')
        status = request.GET.get('status', 'Pending')

        valid_statuses = ['Pending', 'Completed', 'Cancelled']
        if status not in valid_statuses:
            return JsonResponse({'error': 'Invalid order status'}, status=400)

        if user_id == 0 or not start_date or not end_date:
            return JsonResponse({'error': 'Required parameters: userId, startDate, endDate'}, status=400)

        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)

        orders = Order.objects.filter(
            user_id=user_id,
            order_date__gte=start_date,
            order_date__lte=end_date,
            status=status
        )

        order_list = []

        for order in orders:
            order_products = OrderProduct.objects.filter(order=order).select_related('product')

            order_data = {
                'id': order.id,
                'order_date': order.order_date,
                'status': order.status,
                'order_products': [
                    {
                        'product_id': op.product.id,
                        'product_name': op.product.name,
                        'quantity': op.quantity,
                    } for op in order_products
                ]
            }
            order_list.append(order_data)

        return JsonResponse(order_list, safe=False)

    except Exception as e:
        return JsonResponse({'error': 'Error retrieving user orders', 'details': str(e)}, status=500)

