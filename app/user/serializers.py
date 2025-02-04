"""
    serializes for the user api view
"""


from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    #serialzier must know which model is represented
    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        #write only means api wont return as result
        extra_kwargs = {"password" : {"write_only" : True , "min_length" : 5} }

    # we override the create function of the serializer
    # this method will be called only if input is validated
    def create(self,validated_data):
        """create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance , validated_data):
        """update and return user"""
        password = validated_data.pop("password",None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user



class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""

    #field definitions
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type" : "password"},
        trim_whitespace=False
    )

    def validate(self,attrs):
        """Validate and authenticate user"""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            msg = _("Unable to authentiacate user!")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs