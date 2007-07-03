from django.http import HttpResponse, HttpResponseRedirect
from www.memebot.models import *
import www.settings
from django.template import Context, loader
import datetime
import os
from django.core.cache import cache
import re
from django.db.models import Q

def root(request, *args, **kwargs):
	return HttpResponseRedirect('/url/1')

def url(request, *args, **kwargs):
	"""
	Perform some sanity checking
	"""
	if kwargs.has_key('page'):
		page = int(kwargs['page'])
	else:
		return HttpResponseRedirect('/url/1/')

	if page < 1 or page > 365:
		return HttpResponseRedirect('/url/1/')



	"""
	Calculate date range to show and load those URLs up
	"""
	start = datetime.date.today() - datetime.timedelta(days=(page-1))
	end   = start + datetime.timedelta(days=1)
	urls = URL.objects.filter(posted__range=(start, end)).order_by('-id')

	"""
	Image filter
	"""
	toggles = [
		'<a href="/url/%s/img/">Images Only</a>' % page,
		'<a href="/url/%s/youtube/">YouTube Only</a>' % page,
	]

	filter = None
	if kwargs.has_key('img'):
		urls = urls.filter(
			Q(url__endswith='.jpg')  |
			Q(url__endswith='.jpeg') |
			Q(url__endswith='.gif')  |
			Q(url__endswith='.tiff') |
			Q(url__endswith='.png')
		)

		toggles = ['<a href="/url/%s/">All Links</a>' % page]
		filter = 'img'

	elif kwargs.has_key('youtube'):
		urls = urls.filter(url__contains='youtube.com')
		toggles = ['<a href="/url/%s/">All Links</a>' % page]
		filter = 'youtube'


	"""
	These are for navigation links
	"""
	date = start.strftime('%A, %B %d, %Y')

	if page == 1:
		newer = None
		today = None
	else:
		newer = '/url/' + str(page - 1)
		today = '/url/1'

	if page == 2:
		newer = None

	older = '/url/' + str(page + 1)

	if filter is not None:
		if older is not None:
			older += '/%s' % filter

		if newer is not None:
			newer += '/%s' % filter

		if today is not None:
			today += '/%s' % filter

	"""
	Render content and return
	"""
	t = loader.get_template('index.html')
	c = Context({
		'urls'	: urls,
		'date'	: date,

		'older'	: older,
		'today'	: today,
		'newer'	: newer,
		'toggles': toggles,
	})
	return HttpResponse(t.render(c))


def authors(request, *args, **kwargs):
	authors = cache.get('authors')
	if authors is None:
		authors = [(a, a.count) for a in Author.objects.all()]
		authors = sorted(authors, lambda x, y: cmp(y[1], x[1]))
		cache.set('authors', authors, 900)

	if kwargs.has_key('top'):
		authors = authors[:kwargs['top']]
		top = True
	else:
		top = False

	t = loader.get_template('authors.html')
	c = Context({
		'authors'	: authors,
		'top'		: top,
	})

	return HttpResponse(t.render(c))

def top(request, *args, **kwargs):
	return authors(request, top=10)


def author(request, *args, **kwargs):
	try:
		author = Author.objects.get(id=int(kwargs['id']))
	except:
		return HttpResponseRedirect('/author/')


	urls = author.url_set.order_by('-id')

	toggles = [
		'<a href="/author/%s/img/">Images Only</a>' % kwargs['id'],
		'<a href="/author/%s/youtube/">YouTube Only</a>' % kwargs['id'],
	]

	filter = None
	if kwargs.has_key('img'):
		urls = urls.filter(
			Q(url__endswith='.jpg')  |
			Q(url__endswith='.jpeg') |
			Q(url__endswith='.gif')  |
			Q(url__endswith='.tiff') |
			Q(url__endswith='.png')
		)

		toggles = ['<a href="/author/%s/">All Links</a>' % kwargs['id']]
		filter = 'img'

	elif kwargs.has_key('youtube'):
		urls = urls.filter(url__contains='youtube.com')
		toggles = ['<a href="/author/%s/">All Links</a>' % kwargs['id']]
		filter = 'youtube'


	t = loader.get_template('author.html')
	c = Context({
		'author'	: author,
		'urls'		: urls,
		'toggles'	: toggles,
	})

	return HttpResponse(t.render(c))


