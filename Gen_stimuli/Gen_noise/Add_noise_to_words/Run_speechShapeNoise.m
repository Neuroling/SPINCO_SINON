clear all ; 
%% ========================================================================
%  Generate Speech in Speech-shaped noise   
% ========================================================================
% Author: G.FragaGonzalez 2022(based on snippets from T.Houweling)
% Description
%   - Reads list of .wav files 
%   - Filters signal (butterworth), 
%   - Normalize 
%   - Concatenate 
%   - Generate speech shaped noise-SSN
%   - Adjust speech intensity to different levels
%   - SiSSN: adds the noise (optional:  a head and a tail and ramps)
%   - Plots summary figures  
%
%-------------------------------------------------------------------------
% add paths of associated functions and toolbox TSM required by function 
addpath('V:\gfraga\scripts_neulin\Generate_noise\functions')
addpath('V:\gfraga\scripts_neulin\Generate_noise\functions\mp3readwrite')
addpath('C:\Program Files\MATLAB\R2021a\toolbox\MATLAB_TSM-Toolbox_2.03')
addpath('C:\Users\gfraga\Documents\MATLAB\')
addpath('V:\gfraga\scripts_neulin\Generate_noise\functions\mp3readwrite')

%% Inputs 
makeplots = 0;
% paths and files 
dirinput =      'V:\spinco_data\AudioRecs\LIRI_voice_DF\segments\Take1_all_trimmed\trim_loudNorm-23LUFS' ;
diroutput =     'V:\spinco_data\AudioRecs\LIRI_voice_DF\segments\Take1_all_trimmed\trim_loudNorm-23LUFS_SiSSN_15db\' ;
mkdir(diroutput)
cd (dirinput)
audiofiles =      dir(['*.wav']); % must be more than one 
audiofiles =      fullfile(dirinput, {audiofiles.name}); 
 
% Filter settings (butterworth filter lower and upper cut freqs in Hz)
filt_low =      70 ;
filt_upper =    5000;

% Length of intro/outro (with ramp in/out)
head_length =   0.1; % desired start noise length in seconds % 
tail_length =   0; % desired tail noise length in seconds
rampin_length =   0.02; % desired start noise length in seconds
rampout_length =   0; % desired tail noise length in seconds

% Parameters for SSN function
nfft =          1000;
srate =         44100;
noctaves =      6;   % 1/6 octave band smoothing (spectral smoothing in which the bandwidth of the smoothing window is a constant percentage of the center frequency).

% SNR levels
 target_dB_snr = [-10,-7.5,-5,-2.5,0];
 target_dB_snr = [15];
%% Generate noise from concatenated data

% Filter
[signals, fss] = cellfun(@(x) audioread(x), audiofiles, 'UniformOutput',0);
if fss{1}~=srate 
    error('wrong sampling rate specified!')
end 

NyqFreq = srate/2;            % fs = 2kHz; Nyquist freq. = 1 kHz
[filt_b,filt_a]=butter(3, [filt_low filt_upper]/NyqFreq); % make butterworth filter
sigs_filt = cellfun(@(x) filtfilt(filt_b,filt_a,x), signals,'UniformOutput',0);

 % Concatenate speech signal to generate noise
 sigs_filt_concat = vertcat(sigs_filt{:});
 
 % speech-shape noise
 ssn = speechshapednoise(sigs_filt_concat,nfft,noctaves,srate);
 audiowrite([diroutput,'ssn.wav'],ssn,srate,'BitsPerSample',16,'comment','speech-shaped noise with length of all files in folder concatenated');        

 disp('...generated speech-shaped noise from concatenated files '); 
 
 %% Loop thru SNR values and embed  the speech in SSN  
 for L=1:length(target_dB_snr)
     disp('....Starting SNR loop');       
 
   % set up the signal manipulation (see later below)
    dblevel = target_dB_snr(L); 
    target_lin_snr = db2mag(dblevel);  % db2mag matlab func does: 10.^(target_dB_SNR/20);    
    
    
    %%% Add noise to each file  with intro and outro noise and ramps     
    sigs_filt_adj = cell(length(sigs_filt),1);
    SiSSN= cell(length(sigs_filt),1);
     for i = 1:length(sigs_filt)              
      %%%% get a noise segment
         % Define intro and outro and ramps
         head_points = head_length * srate;
         tail_points = tail_length * srate;
         rampin = [linspace(0,1,rampin_length*srate ),ones(1,head_points-rampin_length*srate)];
         rampout = [flip(linspace(0,1,rampout_length*srate)),zeros(1,tail_points-rampout_length*srate)];
         if head_points + tail_points + length(sigs_filt_adj{i}) > length(ssn)
             error('You tried to add too long head/tail noise periods');
         end
                         
      %%%% add noise to signal
         % adjust signal intensity
         sigs_filt_adj{i} = sigs_filt{i}.*target_lin_snr;
         
         %Cut noise chunk
         noise2use_points = head_points + length(sigs_filt_adj{i})+ tail_points;
         seed = randperm(length(ssn)-noise2use_points) ;%find a random data point(prevent out of bounds)
         noise2use = ssn(seed(1):seed(1)+noise2use_points); % take that noise segment
         
         % normalize noise to current signal rms         
         noise2use_norm = noise2use.*(rms(sigs_filt{i})/rms(noise2use));       
                  
         %Speech in Speech-shaped noise:
         SiSSNpart = sigs_filt_adj{i}' + noise2use_norm(1+head_points:head_points+length(sigs_filt_adj{i}));
         ssn_head = noise2use_norm(1:head_points);
         ssn_tail = noise2use_norm((end-tail_points)+1:end);
         sissn = [ssn_head.*rampin, SiSSNpart, ssn_tail.*rampout];              
         disp(['Applying SNR: ', num2str(target_dB_snr(L)) ,'db to file: ' audiofiles{i}])
         
%         % Normalize SiSSN to some db avoiding clipping in any file
%         desired_db  = -25;
%         desired_db_mag = db2mag(desired_db);
%         scaling_factor = sqrt((length(sissn)*desired_db_mag^2)/(sum(sissn.^2)));
%          SiSSN{i,1} = sissn.*scaling_factor;
         
           %Normalize to perceived loudness            
           target_loudnessDB = -23;
           SiSSN{i,1} =  normalize_by_perceivedLoudness(sissn',fss{i},target_loudnessDB);

         % prevent clipping only if needed 
           if any(SiSSN{i,1}>0.99 | SiSSN{i,1} < -0.99)
                 SiSSN{i,1} = SiSSN{i,1}*(0.999999/max(abs(SiSSN{i,1})));  
                 disp('preventing clipping')
           end
     end
      
     
   %% Save audio (and plots if requested)
     audio2save= cell(length(SiSSN),1);
     for i = 1:length(SiSSN)
         
         %%% Save audio (speech in speech-shaped noise
         %--------------------------------------------
         [pathstr, name , ext] = fileparts(audiofiles{i});
         outputfilename = strrep([diroutput,'SiSSN_',name,num2str(dblevel),'db',ext],'\\','\');
         text = ['Speech in speech-shaped noise with ',num2str(target_dB_snr(L)),' SNR db. Normalized at ',num2str(target_loudnessDB),'db. MinF ',num2str(filt_low),' MaxF ',num2str(filt_upper)];
         audiowrite(outputfilename, SiSSN{i},srate,'BitsPerSample',16,'comment',text);        
         disp(['...saved ',outputfilename]);
        
         if makeplots == 1 
             %%% Figures of original and SiSSN
             %---------------------------------------
             SiSSN2plot = SiSSN{i};
             original2plot = audioread(audiofiles{i})';
             variables2plot = {'original2plot','SiSSN2plot'};
             footnote = ['SSN from ', num2str(length(audiofiles)),' files (srate: ',num2str(srate),' Hz) concat and filt (',num2str(filt_low),...
                 ' ',num2str(filt_upper),' Hz). Extra noise intro (', num2str(head_length),' s), outro (', num2str(tail_length),' s) with ramps.',...
                 ' Noct ',num2str(noctaves),'. NFFT ',num2str(nfft),'. SSN norm-',num2str(dblevel),'db'];

             % Start figure 
             figure ('position', [1 1 800 800],'color','white');
             annotation('textbox', [0, 0.075, 1, 0], 'string',footnote)

             % PLOTS: Amplitude x  time
             titles = {'speech (filt)','SiSSN(norm)'};
             for p = 1:2
                 subplot(3,2,p);
                 plot(eval(variables2plot{p}))
                 title(titles{p});  ylabel('Amplitude (a.u.)');  xlabel('Time (ms)');
             end
             % PLOTS: Spectral plots
             titles = {'LTAS speech (filt)','LTAS SiSSN (norm)'};
             for p = 1:2
                 subplot(3,2,2+p);
                 iosr.dsp.ltas(eval(variables2plot{p}),srate,'noct',noctaves,'graph',true,'units','none','scaling','max0','win',srate/10);  % requires the IoSR Matlab Toolbox
                 xline(50, '--k'); xline(5000, '--k');
                 title(titles{p});
             end
             % PLOTS: Surf plots
             titles = {'Spectrogram speech(filt)', 'Spectrogram SiSSN(norm)'};
             for p = 1:2
                 subplot(3,2,4 + p);
                 parameter = [];
                 parameter.fsAudio = srate;
                 parameter.zeroPad = srate/10;
                 [spec2plot,f,t] = stft(eval(variables2plot{p})',parameter);
                 surf(t,f,abs(spec2plot));
                 hold on; set(gcf,'renderer','zbuffer'); shading interp; view(0,90); axis tight; caxis([0 02])
                 title(titles{p});
             end

             print(gcf, '-djpeg', strrep(outputfilename,'.wav','.jpg'));
             disp(['....saved figure for ',outputfilename]);
             close gcf
         end
     end %end SiSSN loop   
 end % close noise level loop