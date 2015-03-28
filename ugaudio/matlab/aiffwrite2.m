function aiffwrite2(file, x, sRate)

%aiffwrite2	Write a sound file in Audio Interchange File Format.
%
% aiffwrite2(file,x,sRate)
% Create an AIFF file with sound data x sampled at sRate Hz.  If x
% has multiple columns, then a multi-channel file will be created.
%
% Written by Jean-Marc Moret (moret@elpp1.epfl.ch).
% Adapted for multichannel output by Dave Mellinger (dkm1@cornell.edu).

% From:		moret@elpp1.epfl.ch
% Newsgroups:	comp.soft-sys.matlab
% Subject:	Re: AIFF output of sounds?
% Organization:	Ecole Polytechnique Federale de Lausanne
% 
% How it works: 
% The 96 bit float is formed by a 2 byte exponent and an 8 byte
% mantissa.  The number that it represents is
% 
% 	2^(exponent-offset)*mantissa
% 
% I assume for simplicity that the sampling frequency is rounded to an
% integer, say for example 9 Hz.  Then the mantissa is 1.001000..... and
% the exponent is 3+offset.  But the same real number is represented by
% 0.000000000000000000000000000100100000000...  This is 2 longs [sRate 0]
% with exponent ~32+offset, which I experimentally set to 16414(decimal).

% Expect column vectors.
if (nRows(x) < nCols(x) & nRows(x) > 16)
  disp('aiffwrite2: warning: multiple channels must be in columns.')
end

npts = nRows(x);
nchan = nCols(x);

% open file
fid = fopen(file, 'w');
if (fid < 0)
  error('Cannot open file');
end

% write FORM chunk
fwrite(fid, 'FORM',	'char');
fwrite(fid, 46+npts*2,	'uint32');
fwrite(fid, 'AIFF',	'char');

% write COMM chunk
fwrite(fid, 'COMM',	'char');
fwrite(fid, 18,		'uint32');	% length of this chunk after here
fwrite(fid, nchan,	'uint16');	% number of channels
fwrite(fid, npts,	'uint32');	% number of samples per channel
fwrite(fid, 16,		'uint16');	% sample size
fwrite(fid, 16414,	'uint16');	% sample rate exponent
fwrite(fid, [sRate 0],	'uint32');	% sample rate mantissa

% write SSND chunk
fwrite(fid, 'SSND',	'char');
fwrite(fid, 8 + npts*2,	'uint32');	% length of this chunk after here
fwrite(fid, [0 0],	'uint32');	% offset, ???
fwrite(fid, x.',	'int16');	% column-major, which interleaves chans

% close
fclose(fid);

function nr = nRows(x)
nr = size(x, 1);

function nc = nCols(x)
nc = size(x, 2);