"""TDGam Exception CLasses."""


class TDGamInvalidSelection(Exception):
    """Unable to create a valid selection from selected ops."""

    def __init__(self, msg):
        """Initialize with a message, and the offending Component object.

        :param msg: exception message.
        :type  msg: str
        """
        super(TDGamInvalidSelection, self).__init__()
        self.msg = msg


class TDGamComponentException(Exception):
    """Unable to create a TDGamComponent instance."""

    def __init__(self, msg, component=None):
        """Initialize with a message, and the offending Component object.

        :param msg: exception message.
        :type  msg: str
        :param component: ofending component object.
        :type  component: TDGam.TDGamComponent
        """
        super(TDGamComponentException, self).__init__()
        self.msg = msg
        self.component = component

    def __repr__(self):
        return self.msg


class TDGamInvalidParameterValue(Exception):
    """Unable to translate a parameter of an op."""

    def __init__(self, msg):
        """Initialize with a message, and offending parameter.

        :param msg: exception message.
        :type  msg: str
        """
        super(TDGamInvalidParameterValue, self).__init__()
        self.msg = msg

    def __repr__(self):
        return self.msg


class GamPluginException(Exception):
    """Unable to convert selection using given plugin."""

    def __init__(self, msg, component=None):
        """Initialize with a message, and the offending plugin.

        :param msg: exception message.
        :type  msg: str
        :param component: ofending component object.
        :type  component: TDGam.TDGamComponent
        """
        super(GamPluginException, self).__init__()
        self.msg = msg
        self.component = component

    def __repr__(self):
        return self.msg
