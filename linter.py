#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Alexander Gordeyev
# Copyright (c) 2014 Alexander Gordeyev
#
# License: MIT
#

"""This module exports the Frosted plugin class."""

from io import StringIO
from SublimeLinter.lint import persist, PythonLinter


class Frosted(PythonLinter):

    """Provides an interface to frosted"""

    syntax = 'python'
    cmd = ('frosted@python', '--verbose', '*', '-')
    version_args = '--version'
    version_re = r'(?P<version>\d+\.\d+\.\d+)'
    version_requirement = '>= 1.3.2'
    regex = r"""(?x)
        ^
        .+?  # filename
        :
        (?P<line>\d+)
        :
        (?P<col>\d+)
        :
        (?P<code>(?:(?P<error>E)|(?P<warning>[IW]))\d{3})
        :
        (?P<near>[^:]*)
        :
        (?P<message>.*)
        $
    """
    multiline = False
    line_col_base = (1, 0)
    defaults = {
        '--ignore:': []
    }
    inline_overrides = ('ignore', )
    module = 'frosted.api'
    check_version = True

    # Internal
    reporter = None

    __transform_options = {
        'ignore': 'ignore_frosted_errors'
    }

    def split_match(self, match):
        """Extract and return values from match."""
        match, line, col, error, warning, message, near = super().split_match(match)

        if not near:
            near = None
        else:
            col = None

        return match, line, col, error, warning, message, near

    def check(self, code, filename):
        """Run frosted.check on code and return the output."""
        output = StringIO()
        Reporter = self.get_reporter()

        options = {
            'filename': filename,
            'reporter': Reporter(output, output),
            'verbose': True
        }

        type_map = {
            'ignore': []
        }

        transform = lambda s: self.__transform_options.get(s, s.replace('-', '_'))
        self.build_options(options, type_map, transform)

        if persist.debug_mode():
            persist.printf('{} options: {}'.format(self.name, options))

        self.module.check(code, **options)
        return output.getvalue()

    def get_reporter(self):
        """Return frosted.Reporter. Must be deferred to runtime."""
        if self.reporter is None:
            from frosted.reporter import Reporter
            self.__class__.reporter = Reporter

        return self.reporter
