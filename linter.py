#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Alexander Gordeyev
# Copyright (c) 2014 Alexander Gordeyev
#
# License: MIT
#

"""This module exports the Frosted plugin linter class."""

from io import StringIO
from SublimeLinter.lint import PythonLinter


class Frosted(PythonLinter):

    """Provides an interface to the frosted python module/script."""

    syntax = 'python'
    cmd = ('frosted@python', '--verbose', '*', '-')
    version_args = '--version'
    version_re = r'(?P<version>\d+\.\d+\.\d+)'
    version_requirement = '>=1.2.0'
    regex = r"""(?x)
        ^
        (?:
            .+?  # filename
            :
            (?P<line>\d+)
            :
            (?P<offset>\d+)
            :
            (?P<code>(?:(?P<error>E)|(?P<warning>[IW]))\d{3})
            :
            (?P<near>[^:\r\n]*)
            :
            (?P<message>[^\r\n]*)
            |
            (?P<syntax_error>
                .+?  # filename
                :
                (?P<syntax_error_line>\d+)
                :
                (?:
                    (?P<syntax_error_offset>\d+)
                    :
                )?
                [ ]
                (?P<syntax_error_message>[^\r\n]*)
                (?:
                    \r?\n
                    [^\r\n]*
                    \r?\n
                    [ ]*\^
                    \r?\n
                )?
            )
            |
            (?P<unexpected_error>
                .+?  # filename
                :
                [ ]
                (?P<unexpected_error_message>[^\r\n]*)
            )
        )
    """
    multiline = True
    defaults = {
        '--ignore=,': ''
    }
    inline_overrides = ('ignore', )
    module = 'frosted.api'
    check_version = True

    # Internal
    reporter = None

    def split_match(self, match):
        match, line, col, error, warning, message, near = super().split_match(match)

        if not match:
            return match, line, col, error, warning, message, near

        groups = match.groupdict()

        if groups.get('syntax_error'):
            error = True
            warning = False
            line, offset, message = [
                groups.get('syntax_error_{}'.format(key)) for key in
                ('line', 'offset', 'message')
            ]

            line = int(line) - self.line_col_base[0]

            if offset:
                col = int(offset)
            else:
                col = 0

        elif groups.get('unexpected_error'):
            message = groups.get('unexpected_error_message')
            line, col, error, warning, near = 0, 0, True, False, None

        else:
            col = int(groups.get('offset', 0))

        if near:
            col = None

        return match, line, col, error, warning, message, near

    def check(self, code, filename):
        """Run frosted.check on code and return the output."""

        output = StringIO()
        reporter = self.get_reporter()
        reporter = reporter(output, output)

        self.module.check(code, filename, reporter=reporter, verbose=True)
        return output.getvalue()

    def get_reporter(self):
        """Return frosted.Reporter. Must be deferred to runtime."""

        if self.reporter is None:
            from frosted.reporter import Reporter
            self.__class__.reporter = Reporter

        return self.reporter
