from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from breadcrumbs_sample.templatetag.views import Index, IncludingDynamicURLs, UnpackingAVariableAndMore

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Example:
    # (r'^breadcrumbs_sample/', include('breadcrumbs_sample.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'webui.views.home',name="index"),
    url(r'^someview/$', 'webui.views.someview'),
    url(r'^index/$', Index.as_view(), name="tag-index"),
    url(r'^dynamic/$', IncludingDynamicURLs.as_view(), name="dynamic"),
    url(r'^unpacking/$', UnpackingAVariableAndMore.as_view(), name="unpacking"),

)
