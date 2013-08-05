# Create your views here.
from django.views.generic import TemplateView
from breadcrumbs.utils import register_referer


class IncludeReferer(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(IncludeReferer, self).get_context_data(**kwargs)
        register_referer(self.request)  # Including the referer if it exists
        return context


class IncludingDynamicURLs(IncludeReferer):
    template_name = "dynamic.html"
    pass


class UnpackingAVariableAndMore(IncludeReferer):
    template_name = "unpacking.html"

    def get_context_data(self, **kwargs):
        context = super(UnpackingAVariableAndMore, self).get_context_data(**kwargs)
        extra_params = ("name1", "example.com"), ("name2", "example2.com")
        context["extra_params"] = extra_params
        return context


class Index(TemplateView):
    template_name = "index.html"