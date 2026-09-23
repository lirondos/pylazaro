import logging

from pylazaro.lazaro import Lazaro
from pylazaro.utils import ExtendedInstallationRequired

# A library should not configure logging for the application that imports it
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["Lazaro", "ExtendedInstallationRequired"]
