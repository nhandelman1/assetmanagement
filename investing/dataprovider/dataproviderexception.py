""" Module for data provider Exceptions. """


class DataProviderException(Exception):
    """Data provider exceptions chainer.

    Chains data provider exceptions. These are typically data provider api request or response errors. The initial
    purpose of this exception class is to prevent multiple logs of the same error.

    Attributes:
        is_logged (boolean): the exception chained by an instance of this class has already been logged
    """

    def __init__(self, msg, is_logged: bool = True):
        """ init

        Args:
            msg (str): exception message
            is_logged (boolean): chained exception has been logged. Default True
        """
        super(DataProviderException, self).__init__(msg)
        self.is_logged = is_logged
