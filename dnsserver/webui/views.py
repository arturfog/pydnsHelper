from django.shortcuts import render
from django.http import Http404
# Create your views here.

from webui.models import Host
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_hosts = Host.objects.all().count()

    context = {
        'num_hosts': num_hosts,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


from django.views import generic

class HostListView(generic.ListView):
    model = Host

class HostDetailView(generic.DetailView):
    model = Host


from .forms import PostForm
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'webui/post_edit.html', {'form': form})

def host_detail_view(request, primary_key):
    try:
        host = Host.objects.get(pk=primary_key)
    except Host.DoesNotExist:
        raise Http404('Host does not exist')

    return render(request, 'webui/host_detail.html', context={'host': host})