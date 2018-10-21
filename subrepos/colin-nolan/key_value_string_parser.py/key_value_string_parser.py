# Copyright (c) 2018 Genome Research Limited
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

class StringDictActionParser(Action):
    """
    Parses input in the form `xxx:yyy` or a stringified JSON map as a key value pair.

    Accepts multiple key-value pairs in stringified JSON map.

    e.g.
    ```
    parser.add_argument(f"-{MY_SHORT_PARAMETER}", f"--{MY_LONG_PARAMETER}", action=StringDictParseAction)
    ```
    """
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            value_as_json = json.loads(values)
            if type(value_as_json) is not dict:
                raise ValueError(f"Not an acceptable JSON value: {values}")
            getattr(namespace, self.dest, {}).update(value_as_json)
        except JSONDecodeError:
            if ":" not in values:
                raise ValueError(f"Unable to parse: {values}. Must be in form \"xxx:yyy\"")
            key, value = values.split(":")
            getattr(namespace, self.dest, {})[key] = value
