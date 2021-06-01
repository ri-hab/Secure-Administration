from rest_framework import viewsets
from jumpserver3s.serializers import ServerGroupSerializer,ServerSerializer,CommandsSequenceSerializer,CredentialSerializer
from jumpserver3s.models import CommandsSequence
from app_user.models import ServerGroup,Server,Credential

class ServerGroupViewSet(viewsets.ModelViewSet):
    queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer

class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

class CredentialViewSet(viewsets.ModelViewSet):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer


class CommandsSequenceViewSet(viewsets.ModelViewSet):
    queryset = CommandsSequence.objects.all()
    serializer_class = CommandsSequenceSerializer
