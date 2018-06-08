import django
import json
from django.http import HttpResponse

def handler(request):
    if request.method == 'GET':
        return HttpResponse(get(request))
    elif request.method == 'POST':
        return HttpResponse(post(request))


def post(request):
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    return json_data['pet']


def get(request):
    return HttpResponse("I have received a GET request! The token is " + django.middleware.csrf.get_token(request))
