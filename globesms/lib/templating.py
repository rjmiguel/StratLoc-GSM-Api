"""
Templating support library and renderer configuration.
"""

from restish import templating


def make_templating(app_conf):
    """
    Create a Templating instance for the application to use when generating
    content from templates.
    """
    renderer = make_renderer(app_conf)
    return Templating(renderer)


class Templating(templating.Templating):
    """
    Application-specific templating implementation.

    Overriding "args" methods makes it trivial to push extra, application-wide
    data to the templates without any assistance from the resource.
    """


def make_renderer(app_conf):
    """
    Create and return a restish.templating "renderer".
    """

    # Uncomment for an example of Mako templating support.
    #import pkg_resources
    #import os.path
    #from restish.contrib.makorenderer import MakoRenderer
    #return MakoRenderer(
    #        directories=[
    #            pkg_resources.resource_filename('globesms', 'template')
    #            ],
    #        module_directory=os.path.join(app_conf['cache_dir'], 'template'),
    #        input_encoding='utf-8', output_encoding='utf-8',
    #        default_filters=['unicode', 'h']
    #        )

    # Uncomment for an example of Jinja2 templating support.
    #from restish.contrib.jinja2renderer import Jinja2Renderer
    #from jinja2 import PackageLoader
    #return Jinja2Renderer(
    #        loader=PackageLoader('globesms', 'template'),
    #        autoescape=True
    #        )

    # Uncomment for an example of Genshi templating support.
    #from restish.contrib.genshirenderer import GenshiRenderer
    #import genshi.template.loader
    #return GenshiRenderer(
    #        genshi.template.loader.package('globesms', 'template')
    #        )

    # Uncomment for an example of Tempita templating support.
    #import pkg_resources
    #from restish.contrib.tempitarenderer import TempitaRenderer, TempitaFileSystemLoader
    #return TempitaRenderer(
    #        TempitaFileSystemLoader(
    #            pkg_resources.resource_filename('globesms', 'template')
    #            )
    #        )

    return None

