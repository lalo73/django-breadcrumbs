#! coding: utf-8
from django import template

register = template.Library()


#http://stackoverflow.com/questions/4356329/creating-a-python-dictionary-from-a-line-of-text/4356415#4356415
def pairwise(iterable):
    #s -> (s0,s1), (s2,s3), (s4, s5), ...
    a = iter(iterable)
    return zip(a, a)


@register.inclusion_tag('breadcrumbs/partial/breadcrumb.html', takes_context=True)
def breadcrumbs(context, *args, **kwargs):
    """
    This tag renders all breadcrumbs registered.
    But you can pass some arguments too.

    If you pass one parameter, it will be shown without an anchor, just what you write.
    i.e.:
        {% breadcrumb "profile" %} or {% breadcrumb  my_context_var %} will print
        each breadcrumb registered and "profile" or what is in 'my_context_var' variable.

    e.g.: Registering two breadcrumb (see "utils.py" module):

        {% breadcrumb "profile" %}
        =>
            <a href="http://eg1.example.com"> breadcrumb_1</a> &gt;
            <a href="http://eg2.example.com"> breadcrumb_2</a> &gt;
            <span> profile</span> &gt;

    If you pass more that one parameter, it takes in pairs. The first must be the what you
        want to show in the breadcrumb, and the second the url. If you pass a odd number of
        parameters, the last must be a "name".
        i.e.: You can do:
            {% breadcrumb "my foos" list_link %} and
            {% breadcrumb "my foos" list_link "foo_settings" %} and
            {% breadcrumb "my foos" list_link "that foo" foo_url %} and
            {% breadcrumb "my foos" list_link "that foo" foo_url "foo_settings" %} and so on

        e.g.: For readability I supposed no another breadcrumbs, just what I wrote here.
            But you can register breadcrumb and they will be shown before that:

            {% url "foo_detail" foo.id as foo_url %}
            {% url "foo_list" as list %}
            {% breadcrumb "my foos" list "that foo" foo_url "foo_settings" %}
            =>
                <a href="{{ list }}"> my foos </a> &gt;
                <a href="{{ foo_url  }}"> that foo </a> &gt;
                <a span> "foo_settings" </span> &gt;

    If you pass the kwarg "unpack" with value True, the template tag only takes 2 arguments.
        the first a iterable that contains tuple of (name, url,), and the second a extra argument,
        Thar will be shown (just a "name")
        i.e.:
            {% breadcrumb my_context_var unpack=True %} or
            {% breadcrumb my_context_var "settings_foo"  unpack=True %}

        e.g.:
            In some class-based view:
                # ...

                class FooSettings(DetailView):
                    model = Foo
                    template = "foo_settings.html"

                    def get_context_data(self, **kwargs):
                        context = super(FooSettings, self).get_context_data(**kwargs)
                        context["list"] =   ("my_foos", reverse("foos"),), ("foo", reverse("foo", args=[self.object.id,]),)
                        return context

                # ...

            In "foo_settings.html" template:

                {% breadcrumb list unpack=True %}

    """
    template_context = dict()
    unpack = kwargs.get('unpack', False)
    args_list = list(args)
    extras = []
    extra = None
    args_len = len(args_list)

    if unpack:
        if args_len == 0:
            raise TypeError("Tag breadcrumb takes at least one argument with 'unpack=True' option.")
        iterable = args_list.pop(0)
        try:
            for arg in iterable:
                extras.append(arg)
        except TypeError as e:
            raise TypeError("Tag breadcrumbs take a iterable like first parameter with 'unpack=True'. %s" % e)
        args_len = len(args_list)

    if args_len % 2 != 0:
        extra = args_list.pop(-1)

    for name, url in pairwise(args_list):
        extras.append((name, url))

    template_context['breadcrumbs'] = context['request'].breadcrumbs
    template_context['extras'] = extras
    template_context['extra'] = extra
    return template_context


__author__ = 'lgomez'
