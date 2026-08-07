"""Authorization rules.

Authentication answers "who are you" - that is TokenAuthentication's job.
These answer "what may you do", which is a separate question and the one the
original app got wrong: it decided role in the browser, from a substring of the
username, and the API checked nothing at all.

Role comes from the database via Employee.role, which reads the Barista and
Manager specialization tables. A client cannot influence it.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


def role_of(request):
    """The requesting user's role, or None.

    None covers three cases that all deny access: nobody is logged in, the
    User has no linked Employee, or the Employee has neither a Barista nor a
    Manager row.
    """
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return None

    employee = getattr(user, 'employee', None)
    if employee is None:
        return None

    return employee.role


class IsStaff(BasePermission):
    """Any authenticated employee - barista or manager."""

    message = 'You must be signed in as an employee.'

    def has_permission(self, request, view):
        return role_of(request) in ('barista', 'manager')


class IsManager(BasePermission):
    """Managers only. Used for employee records, accounting, and sales history."""

    message = 'This action is restricted to managers.'

    def has_permission(self, request, view):
        return role_of(request) == 'manager'


class IsManagerOrReadOnly(BasePermission):
    """Any employee may read; only managers may write.

    Covers the endpoints a barista needs to do their job but should not be
    able to change - the menu, the recipes, current stock levels.

    SAFE_METHODS is GET, HEAD and OPTIONS.
    """

    message = 'Only managers can change this.'

    def has_permission(self, request, view):
        role = role_of(request)
        if role not in ('barista', 'manager'):
            return False
        if request.method in SAFE_METHODS:
            return True
        return role == 'manager'
