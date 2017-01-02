#!/usr/bin/env python

_POPCONFIG_MFILE_FMT_STR = """function [casSources, strStart, strStop, strPlotType, fhPlot, sPlotParams,fhPostPlot, strOutDir, strSuffix] = popconfig()

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% EXAMPLE 3 (keeps figs alive)
%% strDir = '%s';
%% strTempBasePath = '/data/pad';
%% hFigPlots = popmain(strDir, strTempBasePath);

%%%% SOURCES
casSources = {
    'sams2_accel_%s',...
    'sams2_accel_%s',...
    };

%%%% START/STOP STRINGS
strStart = '%s';
strStop =  '%s';

%%%% FUNCTION HANDLE FOR PLOT
strPlotType = 'powspecdens';
fhPlot = @vibratory_disposal_psd;

%%%% PLOT PARAMS THAT NEED CHANGE
%% %% %%            FreqRes: 0.0500
%% %% %%            WhichAx: 'xyz'
%% %% %%               FLim: [0 200]
%% %% %%           FLimMode: 'auto'
%% %% %%               PLim: [1.0000e-14 1.0000e-04]
%% %% %%           PLimMode: 'auto'
%% %% %%            AxWidth: 594
%% %% %%           AxHeight: 152
%% %% %%         OverlapLim: [0 50]
%% %% %%             Window: 'hanning'
%% %% %%               Nfft: 16384
%% %% %%                 No: 0
sPlotParams.WhichAx = 'xyz';
sPlotParams.FLim = [0 5];
sPlotParams.FLimMode = 'manual';
sPlotParams.PLimMode = 'manual';
sPlotParams.Nfft = 65536;
sPlotParams.No = 32768;
sPlotParams.P = 100 * (sPlotParams.No / sPlotParams.Nfft);

%%%% FUNCTION HANDLE FOR POST PLOT PROCESSING
fhPostPlot = @locPostPlot;

%%%% OUTPUT DIR & SUFFIX
strOutDir = pwd;
[~,str] = fileparts(strOutDir);
und = strfind(str,'_');
strSuffix = lower(str(und(3)+1:end));

%%%% LOCAL POST PLOT FUNCTION -----------------------------------------------
function sdnStartPlot = locPostPlot(hFigPlot, sPlotParams)
sdnStartPlot = strtitle2sdnstart(hFigPlot);"""