#!/usr/bin/env python3

import xml.etree.ElementTree as ET


def modify_header_file(xml_file, out_file, new_data_bname, new_tzero, append_dqm):
    """rewrite header file, replacing data file basename, TimeZero and appending to DQM"""
    tree = ET.parse(xml_file)
    # root = tree.getroot()

    # modify GData file name
    gd = tree.find('GData')
    gd.attrib['file'] = new_data_bname

    # modify TimeZero
    tz = tree.find('TimeZero')
    tz.text = new_tzero

    # append to DataQualityMeasure
    dqm = tree.find('DataQualityMeasure')
    dqm.text = dqm.text + ' ' + append_dqm

    # rewrite header file now (with single-quoted first line fields!)
    tree.write(out_file, encoding='US-ASCII', xml_declaration=True)

    # FIXME this next code is klumsy at best
    # fix first line (single to double quotes)
    with open(out_file) as f:
        lines = f.readlines()
    lines[0] = lines[0].replace("'", '"')
    lines[-1] = lines[-1].rstrip('\n') + '\n'
    with open(out_file, 'w') as f:
        f.writelines(lines)

    # FIXME this next part about changing Windows \r\n to Unix \n line endings is also quite klumsy
    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'

    with open(out_file, 'rb') as open_file:
        content = open_file.read()

    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

    with open(out_file, 'wb') as open_file:
        open_file.write(content)


# xml_file = 'C:/Temp/2020_04_05_00_05_15.785+2020_04_05_00_15_15.803.121f03.header'
# out_file = 'c:/Temp/trash.xml'
# modify_header_file(xml_file, out_file, 'one', 'two', 'three')
