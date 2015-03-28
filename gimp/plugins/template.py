#!/usr/bin/env python   
        
# This tells Python to load the Gimp module     
from gimpfu import *    
        
# This is the function that will perform actual actions 
def my_script_function(image, layer):
    print image
    print layer
    print "Hello from my script!"   
    return  
    
# This is the plugin registration function  
# I have written each of its parameters on a different line     
register(   
    "my_first_script",                                       # Your plugin's main function name, as it will be found in Gimp's Procedure Browser.
                                                             # This means that your plugin will be callable by other plugins, using this function name,
                                                             # (even by a script in a another language)!
    "My first Python-Fu",                                    # Your plugin's "documentation" name, as it will also appears in the Procedure Browser.
                                                             # This name should describe your plugin briefly.
    "This script does nothing and is extremely good at it",  # Plugin's help. Give more detail what kind of function your plugin provides.
    "Michel Ardan",                                          # The name of the author of this plugin.
    "Michel Ardan Company",                                  # Any copyright information needed.
    "April 2010",                                            # The date this version of the plugin was released.
    "<Image>/MyScripts/My First Python-Fu",                  # The path in the menu where your plugin should be found.
    "*",                                                     # The image types supported by your plugin.
    [],                                                      # The list of the parameters needed by your plugin.
    [],                                                      # The results sent back by your plugin.
    my_script_function,                                      # The name of the local function to run to actually start processing,
                                                             # which will be called with a set of parameters.
)           

main()