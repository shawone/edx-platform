"""
Template tags and helper functions for displaying breadcrumbs in page titles
based on the current micro site
"""
from django import template
from django.conf import settings
from microsite_configuration.middleware import MicrositeConfiguration

register = template.Library()


def page_title_breadcrumbs(*crumbs, **kwargs):
    """
    create breadcrumbs, using the specified separator
    """
    separator = kwargs.get("separator", " | ")
    if crumbs:
        return '{}{}{}'.format(separator.join(crumbs), separator, platform_name())
    else:
        return platform_name()

@register.simple_tag(name="page_title_breadcrumbs", takes_context=True)
def page_title_breadcrumbs_tag(context, *crumbs):
    return page_title_breadcrumbs(*crumbs)


@register.simple_tag(name="platform_name")
def platform_name():
    return MicrositeConfiguration.get_microsite_configuration_value('platform_name', settings.PLATFORM_NAME)