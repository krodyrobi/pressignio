from django.shortcuts import get_object_or_404, render, render_to_response

from blog.models import Article

def index(request):
	latest_articles_list = Article.objects.all().order_by('-publication_date')[:10]
	return render_to_response('blog/index.html', {'latest_articles_list': latest_articles_list})

def detail(request, title_slug, year, month):
	article = get_object_or_404(Article, slug=title_slug, publication_date__year=year,
		publication_date__month=month)
	return render_to_response('blog/detail.html', {'article': article})
