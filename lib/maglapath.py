"""Magnetic-Lab Path Module (from Magla Project)

A class for converting between tokens and their platform/location-specific
paths(described in 'TDGam/config/paths.yaml'). Tokens can be made up of other
tokens and combined together to create more complex paths.

A token can be described in the following form:

    1. <token_name>

        In this form, Path will look for a matching key in ../config/paths.json.
"""
import os
import re
import platform

SYSTEM = platform.system().lower()


class Path(str):
    """Basestring-wrapper to allow handling of paths containing tokens."""
    __sep_re = r"(/|\\)"
    __tag_re = r"<\w+>"

    def __init__(self, str_):
        """Initialize a tokenable-bastring.

        :param str_: path string which may contain tokens.
        :type  str_: str
        """
        self.__str = str_
        self.__resolved = self.resolve(self.__str)
        super(Path, self).__init__()

    def __str__(self):
        return self.__resolved

    def __repr__(self):
        return self.__resolved

    def resolve(self, str_):
        """Recursively resolve string containing tokens to its associated path.

        :param str_: the string containing tokens to resolve.
        :type  str_: str
        :return: resolved path.
        :rtype:  str
        """
        if self.resolved(str_):
            return str_

        result = self.process_token(str_)

        # make sure we store the sep used from the json to use in joins later
        sep = re.search(self.__sep_re, str_)
        if sep:
            sep = sep.group(1)
        else:
            sep = os.sep
            # if it's not a path just process as is
            if self.resolved(result):
                # please exit the recursive loop, and thanks for riding!
                return result

        # otherwise split the path into segments then resolve each segment
        # independently
        segs = []

        # resolve first level of tags detected
        for seg in re.split(self.__sep_re, result):
            # TODO: find out why we're getting seps here?
            if re.search(self.__sep_re, seg):
                continue
            token = self.is_token(seg)
            if not token:
                segs.append(seg)
                continue
            segs.append(self.process_token(seg))

        # recurse
        return self.resolve(sep.join(segs))

    def str(self):
        """Return the original string before being resolved.

        :return: the original string.
        :rtype:  str
        """
        return self.__str

    @classmethod
    def process_token(cls, token_candidate):
        """Process a single token.

        :param token_candidate: the str to process.
        :type  token_candidate: str
        :return: the resolved token, or the unchanged input.
        :rtype:  str
        """
        token = cls.is_token(token_candidate)
        if not token:
            # no token identifier detected, leave segment as is
            return token_candidate

        return cls.__read_from_json(token)

    @classmethod
    def resolved(cls, str_):
        """Determine if given str is fully resolved.

        :param str_: the str to check.
        :type  str_: str
        :return: True if the string is fully resolved, False if there are still
            tokens detected.
        :rtype:  bool
        """
        return not re.search(cls.__tag_re, str_)

    @staticmethod
    def is_token(str_):
        """Determine if given str is a token.

        :param str_: the str to check.
        :type  str_: str
        :return: True if the string is in token format, False if not.
        :rtype:  bool
        """
        result = re.search(r"^\<(\S+)\>$", str_)
        if result:
            result = result.group(1)

        return result

    @staticmethod
    def __read_from_json(token_name):
        """Retreive the value of token_name from paths.yaml.

        :param token_name: the token_name to retreieve the value for.
        :type  token_name: str
        :return: value, if it exists or token_name.
        :rtype:  str
        """
        import json
        result = token_name
        with open(os.path.join(os.environ["TDGAM"], "config", "paths.json")) as fobj:

            result = json.load(fobj).get(token_name, token_name)
            # if we get a dict, it means we must select the platform
            if isinstance(result, dict):
                result = result[SYSTEM]

        return result
