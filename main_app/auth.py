from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
 # Assuming you have a custom user model

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        # Check password and approved status
        if check_password(password, user.password) and user.is_active:
            return user
        return None


    def get_user(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, surname, email 
                FROM Users 
                WHERE aid = %s
            """, [user_id])
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'name': user[1],
                    'surname': user[2],
                    'email': user[3],
                    'is_authenticated': True
                }
        return None
