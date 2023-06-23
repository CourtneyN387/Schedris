from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import messages
from functools import wraps
from django.contrib.auth.views import redirect_to_login

def advisor_required(function=None,
                     redirect_field_name=REDIRECT_FIELD_NAME,
                     login_url='/accounts/login'):
    """
    A decorator to check whether a logged-in user is an advisor,
    redirecting them to the student index page if not and displaying an error message.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_active and request.user.is_advisor:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have access to this page.')
                # return redirect_to_login(request.get_full_path(), login_url, redirect_field_name)
                return redirect_to_login('/accounts/login', login_url, redirect_field_name)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator

def student_required(function=None,
                     redirect_field_name=REDIRECT_FIELD_NAME,
                     login_url='/accounts/login'):
    """
    A decorator to check whether a logged-in user is a student,
    redirecting them to the advisor index page if not and displaying an error message.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_active and not request.user.is_advisor:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have access to this page.')
                # return redirect_to_login(request.get_full_path(), login_url, redirect_field_name)
                return redirect_to_login('/accounts/login', login_url, redirect_field_name)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


# /***************************************************************************************
# *  REFERENCES
# *  Title: Django Documentation - View decorators 
# *  URL: https://docs.djangoproject.com/en/3.2/topics/http/decorators/

# *  Title: Stack Overflow - How to return error message in decorator in Django?
# *  URL: https://stackoverflow.com/questions/60479527/how-to-return-error-message-in-decorator-in-django
# *****************************************************************************