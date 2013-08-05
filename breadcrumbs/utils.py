# -*- coding: utf-8 -*-
from django.contrib.flatpages.models import FlatPage
from django.http import Http404
from breadcrumbs import Breadcrumbs, BreadcrumbsNotSet
from django.conf import settings
from django.core.cache import cache
from breadcrumbs import BREADCRUMBS_AUTO_HOME, BREADCRUMBS_HOME_TITLE
from django.utils.translation import ugettext as _
import re

BREADCRUMBS_AUTO_HOME = getattr(settings, 'BREADCRUMBS_AUTO_HOME', False)
BREADCRUMBS_HOME_TITLE = getattr(settings, 'BREADCRUMBS_HOME_TITLE', _(u'Home'))

PAGE_MATCHES = getattr(settings, 'PAGE_MATCHES', dict())
#This must be a dictionary. The key are used like regular expression to match the url.
# The value will be shown in breadcrumb. See the template.
# PAGE_MATCHES  = {
#   r'/': u"Home",
#   r'/foo/': u"Foo page"
# }


if BREADCRUMBS_AUTO_HOME:
    PAGE_MATCHES.update({r'/': BREADCRUMBS_HOME_TITLE})


def register_referer(request):
    """
    In any View, you can register the page where you come from.
    It will be automatically matched PAGE_MATCHES with dictionary.
    If it doesn't match, it wont be added to breadcrumbs
    """
    referer = get_referrer(request)
    if referer:
        name = get_name_from_url(referer)
        if name and (name != BREADCRUMBS_HOME_TITLE):
            request.breadcrumbs(name, referer)


def get_referrer(request):
    return request.META.get('HTTP_REFERER', None)


def get_name_from_url(url):
    """
    If the url matched with any regex, then return the name of that page.
    """
    for page_regex in PAGE_MATCHES:
        if re.search(page_regex, url):
            return PAGE_MATCHES[page_regex]
    return None


def make_flatpages_cache_key():
    """
    Create a cache key based on some basic data, respecting defined site.
    """
    key = "flatpages_cache_%s-%s" % (hash(settings.SITE_ID),
                                      hash(settings.SECRET_KEY))

    return key


def get_flapage_from_cache(url):
    """
    Try get flatpage from cache entry with all flatpages by url.
    If not found, create cache and return flatpage from db.

    This probably avoid some hits on DB.
    """
    site_id = settings.SITE_ID
    cache_key = make_flatpages_cache_key()
    flatpages = cache.get(cache_key)
    if flatpages and url in flatpages:
        return flatpages[url]

    # flatpages cache not exist or flatpage not found.

    # 1. get all flatpages.
    flatpages = dict([(f.url, f) for f in
        FlatPage.objects.filter(sites__id__exact=site_id).order_by('url')])

    # 2. if url not in flatpages, raise Http404
    if url not in flatpages:
        raise Http404

    # 3. if url in flatpages, recreate cache and return flatpage
    cache.delete(cache_key)
    cache.add(cache_key, flatpages)
    return flatpages[url]


def breadcrumbs_for_flatpages(request, flatpage):
    """ given request and flatpage instance create breadcrumbs for all flat
    pages """
    if not hasattr(request, 'breadcrumbs') or \
                            not isinstance(request.breadcrumbs, Breadcrumbs):
        raise BreadcrumbsNotSet(u"You need to setup breadcrumbs to use this "
                                u"function.")

    if not isinstance(flatpage, FlatPage) or not hasattr(flatpage, 'id'):
        raise TypeError(u"flatpage argument isn't a FlatPage instance or not "
                        u"have id.")

    # URL for a flatpage can be composed of other flatpages, ex:
    #
    # We have:
    #   flatpage01 = /flat01/
    #   flatpage02 = /flat01/flat02/
    #   flatpage03 = /flat01/flat02/flat03/
    #
    # In breadcrumbs we want to know each title of each page, so we split url
    # in parts, and try to get flatpage title.
    #
    # However, you can define something like that in your urls.py:
    #   (r'^pages/', include('breadcrumbs.urls')),
    # And, we will never know what is /pages/, so we ignore it for now.
    paths = []
    for part in request.path_info.split(u"/"):
        # When split we have u"" for slashes
        if len(part) == 0:
            continue
        # Add slash agai
        if not part.startswith(u"/"):
            part = u"/" + part
        if not part.endswith(u"/"):
            part = part + u"/"
        # If we have something on paths, url for flatpage is composed of what we
        # have in path + part. Note that strings in path not have last slash, but
        # part have.
        if len(paths) > 0:
            url = u"".join(paths + [part])
        else:
            url = part
        # if part of url is same url of flatpage instance, we don't hit
        # database again, we get page from FlatPage instance.
        # If part of url isn't same url of flatpage instance, we try to get it.
        # If page doesn't exist, we just continue to next part.
        if url == flatpage.url:
            request.breadcrumbs(flatpage.title, flatpage.url)
        else:
            try:
                f = FlatPage.objects.get(url=url)
            except FlatPage.DoesNotExist:
                # TODO: this part can be a view, maybe is a good idea get that
                # view and check for viewfunc.breadcrumb_title or
                # viewclass.breadcrumb_title attributes.
                continue
            else:
                request.breadcrumbs(f.title, f.url)
        # add last part of path in paths with one slash
        paths.append(u"/" + url[1:-1].rpartition(u"/")[-1])
