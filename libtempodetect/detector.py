import librosa
import pretty_midi
import numpy
import mir_eval

from librosa.feature import tempogram, fourier_tempogram
from librosa.util.exceptions import ParameterError



class Detector:

    def __init__( self , file_path ):

        if file_path.suffix == "mid" :

            # pretty_midi doesn't support pathlib.Path
            self.midi_data = pretty_midi.PrettyMIDI( str( file_path ) )

        else:

            self.audio_time_series , self.sampling_rate = librosa.load( file_path )

    def tempo(
        self,
        *,
        y=None,
        sr=22050,
        onset_envelope=None,
        hop_length=512,
        start_bpm=120,
        std_bpm=1.0,
        ac_size=8.0,
        max_tempo=320.0,
        aggregate=numpy.mean,
        prior=None,
        tempogram_method='autocorrelation',
    ):

        # init
        y = self.audio_time_series
        sr = self.sampling_rate   


        if start_bpm <= 0:
            raise ParameterError("start_bpm must be strictly positive")

        win_length = librosa.core.time_to_frames(ac_size, sr=sr, hop_length=hop_length).item()
        
        # https://librosa.org/doc/main/generated/librosa.feature.tempogram.html
        # win_length = 384 * hop_length / sr ~= 8.9s
        # win_length = int( 4 * sr / hop_length )

        
        # Get the tempogram
        if tempogram_method == 'autocorrelation' :
            
            tg = tempogram(
                y=y,
                sr=sr,
                onset_envelope=onset_envelope,
                hop_length=hop_length,
                win_length=win_length,
            )

        elif tempogram_method == 'fourier' :

            tg = fourier_tempogram(
                y=y,
                sr=sr,
                onset_envelope=onset_envelope,
                hop_length=hop_length,
                win_length=win_length,
            )

        else:

            raise ParameterError("tempogram_method argument error")


        # Eventually, we want this to work for time-varying tempo
        if aggregate is not None:
            tg = aggregate(tg, axis=-1, keepdims=True)

        # Get the BPM values for each bin, skipping the 0-lag bin
        bpms = librosa.core.tempo_frequencies(tg.shape[-2], hop_length=hop_length, sr=sr)

        # Weight the autocorrelation by a log-normal distribution
        if prior is None:
            logprior = -0.5 * ((numpy.log2(bpms) - numpy.log2(start_bpm)) / std_bpm) ** 2
        else:
            logprior = prior.logpdf(bpms)

        # Kill everything above the max tempo
        if max_tempo is not None:
            max_idx = numpy.argmax(bpms < max_tempo)
            logprior[:max_idx] = -numpy.inf
        # explicit axis expansion
        logprior = librosa.util.expand_to(logprior, ndim=tg.ndim, axes=-2)

        # Get the maximum, weighted by the prior
        # Using log1p here for numerical stability
        best_period = numpy.argmax(numpy.log1p(1e6 * tg) + logprior, axis=-2)

        #
        period = numpy.log1p(1e6 * tg) + logprior

        # [ fast , slow ]
        period_return = []
        
        # Get the maximum , unpack index
        maximum = numpy.take(bpms, best_period)[0]

        period_return.append( maximum )

        # Get the second largest , unpack index
        second_largest = numpy.take( bpms, numpy.argsort(period, axis=0)[-2] )[0]

        period_return.append( second_largest )
        

        return period_return

    def beat( self ) -> numpy.ndarray:
        
        # Track beats
        tempo, beats = librosa.beat.beat_track( y=self.audio_time_series , sr=self.sampling_rate )

        # frames to timestamps
        beats_timestamps = librosa.frames_to_time( beats , sr=self.sampling_rate )


        return beats_timestamps


class Score:
    
    def __init__( self , reference_tempo , estimated_tempo_fast , estimated_tempo_slow ):
         
        self.reference_tempo = reference_tempo
        self.estimated_tempo_fast = estimated_tempo_fast
        self.estimated_tempo_slow = estimated_tempo_slow
        
        
    def p( self ) -> int:
        """
        Compute P-score.

        :rtype: int
        """

        condition_1 = abs( ( self.reference_tempo - self.estimated_tempo_slow ) / self.reference_tempo ) <= 0.08
        condition_2 = abs( ( self.reference_tempo - self.estimated_tempo_fast ) / self.reference_tempo ) <= 0.08

        #
        if condition_1 and condition_2 :

            score = 1

        else:

            score = 0


        return score

    def alotc( self ) -> int:
        """
        Compute ALOTC score.

        :rtype: int
        """
        
        condition_1 = abs( ( self.reference_tempo - self.estimated_tempo_slow ) / self.reference_tempo ) <= 0.08
        condition_2 = abs( ( self.reference_tempo - self.estimated_tempo_fast ) / self.reference_tempo ) <= 0.08

        #
        if condition_1 or condition_2 :

            score = 1

        else:

            score = 0


        return score




















