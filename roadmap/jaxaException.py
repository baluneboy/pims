#!/usr/bin/env python
# $Id$

import exceptions


#Exception class
class jaxaException(Exception):
    """Base class for exceptions in CMT module."""
    def __init__(self,args=None):
        self.args = args

#File Errors
class jaxaFileError(jaxaException):
    """Class for file errors in CMT module."""
    pass

class jaxaFileNameError(jaxaFileError):
    """Class for filename parse errors in CMT module."""
    pass

class jaxaFileIdError(jaxaFileError):
    """Class for file Id errors in CMT module."""
    pass

class jaxaParameterIdError(jaxaFileNameError):
    """Class for Paramter Id parse errors in CMT module."""
    pass

# Data Errors
class jaxaDataError(jaxaException):
    """Class for data errors in CMT module."""
    pass

class jaxaDataIDError(jaxaDataError):
    """Class for data id (primary key) errors in CMT module."""
    pass

class jaxaDataTypeError(jaxaDataError):
    """Class for data type errors in CMT module."""
    pass
