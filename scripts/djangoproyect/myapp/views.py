from django.http import HttpResponse, JsonResponse
from .models import Project, Task
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    title = "Django curso"
    #return HttpResponse("index page")
    return render(request, "index.html", {
        "title": title
    })

def hello(request, username):
    #print(username)
    #return HttpResponse("Hello " + username)
    return HttpResponse("<h2> Hello %s</h2>" % username)

def about(request):
    username = "paco"
    return render(request, "about.html",{
        "username": username
    })

def projects(request):
    #projects = list(Project.objects.values())
    projects = Project.objects.all()
    #return JsonResponse(projects, safe=False)
    return render(request, "Projects.html",{
        "projects": projects
    })

def tasks(request,id):
    #task = Task.objects.get(id=id)
    # task = get_object_or_404(Task,id=id)
    #return HttpResponse("taks: %s" % task.title)
    tasks = Task.objects.all()
    return render(request, "tasks.html",{
        "tasks":tasks
    })

def login(request):

    if request.method == 'GET':
        return render(request, "signup.html",{
        "form" : UserCreationForm
    })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.post['username'],password=request.post['password1'])
                user.save()
                return HttpResponse("Usuario creado")
            except:
                return HttpResponse("El usuario ya existe")
        return HttpResponse("Password no coinciden")
