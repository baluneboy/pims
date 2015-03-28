function padwrite(data, strFile)

% EXAMPLE
% fs = 44100; % CD quality audio
% t = 0:1/fs:1-(1/fs);
% Ax = 1; x = Ax*sin(2*pi*40*t);
% Ay = 1; y = Ay*sin(2*pi*80*t);
% Az = 1; z = Az*sin(2*pi*5000*t);
% data = [t(:) x(:) y(:) z(:)];
% strFile = '/tmp/test1.pad';
% padwrite(data, strFile);
%
% Ax = 1; x = Ax*chirp(t, 10, 0.9, 5000);
% Ay = 1; y = Ay*sin(2*pi*60*t);
% Az = 1; z = Ax*chirp(t, 100, 0.9, 200);
% data = [t(:) x(:) y(:) z(:)];
% strFile = '/tmp/test2.pad';
% padwrite(data, strFile);

%Author: Ken Hrovat, 10/29/14
%$Id$

% With one arg, use that as stub for 3 filenames (x,y,z)
if nargin == 1
    strFile = [data '.pad'];
    [x, fsx] = audioread([data 'x.aiff']);
    [y, fsy] = audioread([data 'y.aiff']);
    [z, fsz] = audioread([data 'z.aiff']);
    if fsx == fsy && fsy == fsz
        t = 0:1/fsx:(length(x)-1)/fsx;
    end
    data = [t(:) x(:) y(:) z(:)];
end
    
% Write pad file
fid = fopen(strFile,'w','l');
count = fwrite(fid,data','float');
fclose(fid);

fprintf('\nWrote %d records to PAD file %s\n', count, strFile)