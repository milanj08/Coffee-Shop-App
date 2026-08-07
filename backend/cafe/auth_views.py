"""Authentication endpoints: register, login, logout, me.

Kept in their own module rather than added to the 300-line views.py, because
these are about identity and everything in views.py is about coffee.
"""

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AccountSerializer, RegisterSerializer


def _account_payload(employee, token):
    """One response shape for register, login, and me, so the frontend has one
    thing to parse."""
    data = AccountSerializer(employee).data
    if token is not None:
        data['token'] = token
    return data


class RegisterAPIView(APIView):
    """POST /api/auth/register/ - open signup, always creates a barista."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()

        # Issued here so signing up logs you straight in. The alternative -
        # register, then post the credentials again - is two round trips for
        # no benefit.
        token, _ = Token.objects.get_or_create(user=employee.user)

        return Response(
            _account_payload(employee, token.key),
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    """POST /api/auth/login/ - exchange username and password for a token."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # authenticate() runs Django's password hasher against the stored hash.
        # It returns None for both "no such user" and "wrong password", and the
        # response says the same thing for both on purpose - distinguishing
        # them tells an attacker which usernames exist.
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'detail': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        employee = getattr(user, 'employee', None)
        if employee is None or employee.role is None:
            # Authenticated, but not an employee of this shop - so there is
            # nothing they are allowed to do. 403, not 401: we know who they
            # are, they just have no role.
            return Response(
                {'detail': 'This account is not linked to an employee record.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(_account_payload(employee, token.key))


class LogoutAPIView(APIView):
    """POST /api/auth/logout/ - destroy the caller's token.

    DRF tokens never expire on their own, so logging out has to delete it
    server-side. Clearing localStorage alone would leave a valid token that
    still works if anyone copied it.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(APIView):
    """GET /api/auth/me/ - who am I, and what am I allowed to do?

    The frontend calls this on page load to restore a session from a stored
    token. It is also how the client learns its role - it never decides that
    for itself.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = getattr(request.user, 'employee', None)
        if employee is None or employee.role is None:
            return Response(
                {'detail': 'This account is not linked to an employee record.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(_account_payload(employee, None))
