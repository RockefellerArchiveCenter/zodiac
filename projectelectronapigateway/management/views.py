import json
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .forms import apiURLForm
from django.shortcuts import render, redirect


@csrf_exempt
def index(request):
    return HttpResponse(get_URL(request))


@csrf_exempt
def get_URL(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = apiURLForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            print(checkForBag(form['url1'].value()))

            # currently trying to get value from database
            url = apiURL.objects

            return render(request, 'management/results.html', {'form': form})

    # if a GET (or any other method) call apiURLForm
    else:
        form = apiURLForm()
    return render(request, 'management/name.html', {'form': form})


def checkForBag(url):
    r = requests.get(url)
    return r.text


def receiveBag(request):
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    return json.dumps(json_data, indent=4, sort_keys=True)


def sendBag(request):
    # Takes in valid bag from POST
    contentbag = receiveBag(request)
    # Send bag via POST to Aquarius
    response = requests.post(URL, data=contentbag)
    content = response.content
    print("Sending data to Aquarius...")
    return HttpResponse("The JSON was sent to " + content)
