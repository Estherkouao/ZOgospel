from .models import Actualite

def latest_actualites(request):
    latest = Actualite.objects.all().order_by('-date')[:4]
    return {'latest_actualites': latest}
