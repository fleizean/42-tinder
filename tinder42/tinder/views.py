from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from .models import UserProfile, Interaction, MatchPreferences
from .forms import UserProfileForm, MatchPreferencesForm
from .utils import get_upload_to
from indianpong.settings import BASE_URL
import random, os, uuid

@never_cache
def index(request):
    return render(request, 'index.html')

@never_cache
def auth(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    auth_url = "https://api.intra.42.fr/oauth/authorize"
    fields = {
        "client_id": environ.get("FT_CLIENT_ID"),
        "redirect_uri": f"{BASE_URL}/auth_callback",  # This should be parameterized
        "scope": "public",
        # "state": state_req,  # This will generate a 50-character long random string
        "response_type": "code",
    }
    encoded_params = urlencode(fields)
    url = f"{auth_url}?{encoded_params}"
    return redirect(url)

    
@never_cache
def auth_callback(request):
    # Handle the callback from 42 and exchange the code for an access token
    if request.method == "GET":
        # Create a context that doesn't verify SSL certificates
        # Create a SSL context
        # ssl_context = ssl.create_default_context()

        # Load your certificate
        # ssl_context.load_cert_chain(certfile='path/to/certfile', keyfile='path/to/keyfile')
        ssl_context = ssl._create_unverified_context()  # TODO temporary solution
        code = request.GET.get("code")
        data = {
            "grant_type": "authorization_code",
            "client_id": environ.get("FT_CLIENT_ID"),
            "client_secret": environ.get("FT_CLIENT_SECRET"),
            "code": code,
            "redirect_uri": "http://localhost:8000/auth_callback",
        }
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(
            "https://api.intra.42.fr/oauth/token", data=encoded_data
        )
        response = urllib.request.urlopen(
            req, context=ssl_context
        )  # TODO temporary solution

    # Process the response, store the access token, and authenticate the user
    if response.status == 200:
        token_data = json.loads(response.read().decode("utf-8"))
        """with open('token_data.json', 'w') as file:
            json.dump(token_data, file)"""
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        created_at = token_data.get("created_at")
        secret_valid_until = token_data.get("secret_valid_until")

        # Fetch user information from 42 API
        headers = {"Authorization": f"Bearer {access_token}"}
        req = urllib.request.Request("https://api.intra.42.fr/v2/me", headers=headers)
        user_info_response = urllib.request.urlopen(
            req, context=ssl_context
        )  # TODO temporary solution

        if user_info_response.status == 200:
            user_data = json.loads(user_info_response.read().decode("utf-8"))
            """with open('user_data.json', 'w') as file:
                json.dump(user_data, file) """

            

            if UserProfile.objects.filter(email=user_data["email"]).exists():
                user = UserProfile.objects.get(email=user_data["email"])
            else:
                user, created = UserProfile.objects.get_or_create(
                    username=user_data["login"]
                )
                if not created:
                    user = UserProfile.objects.create(
                        username=user_data["login"] + "42"
                    )
                else:
                    # Update user profile
                    user.set_unusable_password()
                    user.displayname = user_data.get("displayname", "")
                    user.email = user_data.get("email", "")
                    user.is_42student = True
                    user.kind = user_data.get("kind", "")
                    campus_list = user_data.get("campus", [])
                    if campus_list:
                        user.campus = campus_list[0].get("name", "")
                        user.location = campust_list[0].get("city", "")
                    curses_users_list = user_data.get("cursus_users", [])
                    if curses_users_list:
                        user.level = curses_users_list[0].get("level", 1)
                    
                    image_url = (
                        user_data.get("image", {}).get("versions", {}).get("medium", "")
                    )
                    if image_url:
                        image_name, response = urllib.request.urlretrieve(image_url)
                        file = File(open(image_name, "rb"))
                        user.avatar.save(f"{file.name}.jpg", file, save=False)
                        file.close()
                    user.save()

                    # Store the access token in the OAuthToken model
                    oauth_token = OAuthToken.objects.create(
                        user=user,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        expires_in=expires_in,
                        created_at=created_at,
                        secret_valid_until=secret_valid_until,
                    )
                    oauth_token.save()

            # Log in the user
            login(request, user)
            return redirect("dashboard")

    return redirect("login")  # Handle authentication failure