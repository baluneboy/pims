#!/usr/bin/env python

# extracting_nested_tars.py

import os
import re
import tarfile

file_extensions = ('tar', 'tgz')
# Edit this according to the archive types you want to extract. Keep in
# mind that these should be extractable by the tarfile module.

def FileExtension(file_name):
    """Return the file extension of file

    'file' should be a string. It can be either the full path of
    the file or just its name (or any string as long it contains
    the file extension.)

    Examples:
    input (file) -->  'abc.tar'
    return value -->  'tar'

    """
    match = re.compile(r"^.*[.](?P<ext>\w+)$",
      re.VERBOSE|re.IGNORECASE).match(file_name)

    if match:           # if match != None:
        ext = match.group('ext')
        return ext
    else:
        return ''       # there is no file extension to file_name

def AppropriateFolderName(folder_name, parent_fullpath):
    """Return a folder name such that it can be safely created in
    parent_fullpath without replacing any existing folder in it.

    Check if a folder named folder_name exists in parent_fullpath. If no,
    return folder_name (without changing, because it can be safely created 
    without replacing any already existing folder). If yes, append an
    appropriate number to the folder_name such that this new folder_name
    can be safely created in the folder parent_fullpath.

    Examples:
    folder_name = 'untitled folder'
    return value = 'untitled folder' (if no such folder already exists
                                      in parent_fullpath.)

    folder_name = 'untitled folder'
    return value = 'untitled folder 1' (if a folder named 'untitled folder'
                                        already exists but no folder named
                                        'untitled folder 1' exists in
                                        parent_fullpath.)

    folder_name = 'untitled folder'
    return value = 'untitled folder 2' (if folders named 'untitled folder'
                                        and 'untitled folder 1' both
                                        already exist but no folder named
                                        'untitled folder 2' exists in
                                        parent_fullpath.)

    """
    if os.path.exists(os.path.join(parent_fullpath,folder_name)):
        match = re.compile(r'^(?P<name>.*)[ ](?P<num>\d+)$').match(folder_name)
        if match:                           # if match != None:
            name = match.group('name')
            number = match.group('num')
            new_folder_name = '%s %d' %(name, int(number)+1)
            return AppropriateFolderName(new_folder_name,
                                         parent_fullpath)
            # Recursively call itself so that it can be check whether a
            # folder named new_folder_name already exists in parent_fullpath
            # or not.
        else:
            new_folder_name = '%s 1' %folder_name
            return AppropriateFolderName(new_folder_name, parent_fullpath)
            # Recursively call itself so that it can be check whether a
            # folder named new_folder_name already exists in parent_fullpath
            # or not.
    else:
        return folder_name

def Extract(tarfile_fullpath, delete_tar_file=True):
    """Extract the tarfile_fullpath to an appropriate* folder of the same
    name as the tar file (without an extension) and return the path
    of this folder.

    If delete_tar_file is True, it will delete the tar file after
    its extraction; if False, it won`t. Default value is True as you
    would normally want to delete the (nested) tar files after
    extraction. Pass a False, if you don`t want to delete the
    tar file (after its extraction) you are passing.

    """
    tarfile_name = os.path.basename(tarfile_fullpath)
    parent_dir = os.path.dirname(tarfile_fullpath)

    extract_folder_name = AppropriateFolderName(tarfile_name[:\
    -1*len(FileExtension(tarfile_name))-1], parent_dir)
    # (the slicing is to remove the extension (.tar) from the file name.)
    # Get a folder name (from the function AppropriateFolderName)
    # in which the contents of the tar file can be extracted,
    # so that it doesn't replace an already existing folder.
    extract_folder_fullpath = os.path.join(parent_dir,
    extract_folder_name)
    # The full path to this new folder.

    try:
        tar = tarfile.open(tarfile_fullpath)
        tar.extractall(extract_folder_fullpath)
        tar.close()
        if delete_tar_file:
            os.remove(tarfile_fullpath)
        return extract_folder_name
    except Exception as e:
        # Exceptions can occur while opening a damaged tar file.
        print 'Error occured while extracting %s\n'\
        'Reason: %s' %(tarfile_fullpath, e)
        return

def WalkTreeAndExtract(parent_dir):
    """Recursively descend the directory tree rooted at parent_dir
    and extract each tar file on the way down (recursively).
    """
    try:
        dir_contents = os.listdir(parent_dir)
    except OSError as e:
        # Exception can occur if trying to open some folder whose
        # permissions this program does not have.
        print 'Error occured. Could not open folder %s\n'\
        'Reason: %s' %(parent_dir, e)
        return

    for content in dir_contents:
        content_fullpath = os.path.join(parent_dir, content)
        if os.path.isdir(content_fullpath):
            # If content is a folder, walk it down completely.
            WalkTreeAndExtract(content_fullpath)
        elif os.path.isfile(content_fullpath):
            # If content is a file, check if it is a tar file.
            # If so, extract its contents to a new folder.
            if FileExtension(content_fullpath) in file_extensions:
                extract_folder_name = Extract(content_fullpath)
                if extract_folder_name:     # if extract_folder_name != None:
                    dir_contents.append(extract_folder_name)
                    # Append the newly extracted folder to dir_contents
                    # so that it can be later searched for more tar files
                    # to extract.
        else:
            # Unknown file type.
            print 'Skipping %s. <Neither file nor folder>' % content_fullpath

if __name__ == '__main__':
    tarfile_fullpath = '/home/pims/temp/sams/samslogs014.tgz' # pass the path of your tar file here.
    extract_folder_name = Extract(tarfile_fullpath, False)

    # tarfile_fullpath is extracted to extract_folder_name. Now descend
    # down its directory structure and extract all other tar files
    # (recursively).
    extract_folder_fullpath = os.path.join(os.path.dirname(tarfile_fullpath), extract_folder_name)
    WalkTreeAndExtract(extract_folder_fullpath)
    # If you want to extract all tar files in a dir, just execute the above
    # line and nothing else.
    
    # FIXME next 2 lines show "gz" files could not be opened successfully!?
    file_extensions = ('gz')
    WalkTreeAndExtract(extract_folder_fullpath)