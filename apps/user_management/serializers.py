from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import send_verification_email


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    phone_number = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'password',
            'password2'
        ]

    # validation to check if both passwords match
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    # validation to check if phone number is in correct format
    def validate_phone_number(self, value):
        import re
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError(
                "Phone number must be in format: '+999999999'."
            )
        return value
    

    def create(self, validated_data):
        # Remove password2 before creating user
        validated_data.pop('password2')
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            is_active=False,  # User not active until email verified
        )
        user.set_password(validated_data['password'])
        user.save()
        
        # Send verification email
        send_verification_email(user)
        
        return user

    
    # def create(self, validated_data):
    #     # Remove password2 before creating user
    #     validated_data.pop('password2')
    #     user = User.objects.create(
    #         email=validated_data['email'],
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name'],
    #         phone_number=validated_data['phone_number']
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user



class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        from .utils import is_otp_valid
        if not is_otp_valid(user, otp):
            raise serializers.ValidationError("Invalid or expired OTP.")
            
        attrs['user'] = user
        return attrs


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
            
        attrs['user'] = user
        return attrs
    
    
# Working Custom Token Serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get the username field and recreate it as email field
        username_field = self.fields.get('username')
        if username_field:
            self.fields['email'] = username_field
            del self.fields['username']
            self.fields['email'].label = 'Email'

    def validate(self, attrs):
        # Rename email to username for parent class validation
        email = attrs.get('email')
        if email:
            attrs['username'] = email
        
        # Call parent validation
        data = super().validate(attrs)
        
        # Add custom claims
        data['is_admin'] = self.user.is_superuser
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        
        return data
       