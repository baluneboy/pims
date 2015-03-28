function aiff2pad(strFile)

% EXAMPLE
% strFile = '/Users/ken/dev/programs/python/pims/ugaudio/samples/alex.aiff';
% aiff2pad(strFile);

%Author: Ken Hrovat, 11/02/14
%$Id$

[y,fs] = aiffread(strFile);
t = 0:1/fs:(length(y)-1)/fs;
y = double(y);
x = y;
z = y;
% t = t';
data = [t(:) x(:) y(:) z(:)];
strFile = [strFile '.pad'];
padwrite(data, strFile);