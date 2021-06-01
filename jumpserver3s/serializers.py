from rest_framework import serializers
from jumpserver3s.models import CommandsSequence
from app_user.models import Server,ServerGroup, Credential

class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'

class ServerGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServerGroup
        fields = '__all__'

class CredentialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Credential
        fields = '__all__'

class CommandsSequenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CommandsSequence
        fields = '__all__'
