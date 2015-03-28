function data = padread(strFile)

% PADREAD - read binary PAD files into matrix form
%
% data = padread(strFile);
%
% INPUTS:
% strFile - string full filename
%
% OUTPUT:
% data - matrix with 4 columns [t x y z]; where t is offset from file start
%        time in seconds and remaining columns are 3 orthogonal components
%        of acceleration in units of g
%
% SAMS EXAMPLE:
% strFile = '/tmp/2013_12_09_00_51_11.508+2013_12_09_01_01_11.565.es03';
% data = padread(strFile);
% data(1:5,:)

fid = fopen(strFile,'r','l');
% change 4 in next line to number of columns in PAD data file
% SAMS typically 4; MAMS ossraw data can have more
data = fread(fid,[4 inf],'float')';
fclose(fid);
