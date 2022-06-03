import numpy
import concurrent.futures
import tqdm
import re
import mir_eval

from . import path
from . import detector



class Report:

    def __init__( self ):
        pass

    def __autocorrelation_method( self , reference_tempo , estimated_file_path ):
        
        # create template
        autocorrelation_method_result = { 'P-score': None, 'ALOTC-score': None }

        # compute estimated_tempo
        detector_cls = detector.Detector( estimated_file_path )

        estimated_tempo = detector_cls.tempo( tempogram_method='autocorrelation')

        temp_fast = estimated_tempo[0] 
        temp_slow = estimated_tempo[1] 

        # compute score
        score_cls = detector.Score( reference_tempo , estimated_tempo_fast=temp_fast , estimated_tempo_slow=temp_slow )

        autocorrelation_method_result['P-score'] = score_cls.p()
        autocorrelation_method_result['ALOTC-score'] = score_cls.alotc()
        
        #
        return autocorrelation_method_result

    def __fourier_method( self , reference_tempo , estimated_file_path ):
        
        # create template
        fourier_method_result = { 'P-score': None, 'ALOTC-score': None }

        # compute estimated_tempo
        detector_cls = detector.Detector( estimated_file_path )

        estimated_tempo = detector_cls.tempo( tempogram_method='fourier' )

        temp_fast = estimated_tempo[0] 
        temp_slow = estimated_tempo[1] 

        # compute score
        score_cls = detector.Score( reference_tempo , estimated_tempo_fast=temp_fast , estimated_tempo_slow=temp_slow )

        fourier_method_result['P-score'] = score_cls.p()
        fourier_method_result['ALOTC-score'] = score_cls.alotc()
        
        #
        return fourier_method_result

    def __beats_method( self , estimated_file_path ):
        
        # compute estimated beats
        detector_cls = detector.Detector( estimated_file_path )

        beats_result = detector_cls.beat()


        return beats_result

    def __dict_to_list( self , dict_ ):
        
        temp_list = []

        # create list which need to output
        write_list_method = [ 'autocorrelation','fourier' ]
        write_list_score = [ 'P-score','ALOTC-score' ]

        # convert
        for method in write_list_method:

            for score in write_list_score :

                temp_list.append( dict_[method][score] )

        #
        return temp_list

    def __array_to_dict( self , numpy_array ):
        
        temp_dict = {}

        # create list which need to output
        write_list_method = [ 'autocorrelation','fourier' ]
        write_list_score = [ 'P-score','ALOTC-score' ]

        # convert

        # read index from 0 
        index_array = 0

        for method in write_list_method:

            temp_dict[method] = {}
            
            for score in write_list_score :

                temp_dict[method][score] = numpy_array[ index_array ]

                # next index
                index_array += 1
                    

        #
        return temp_dict

    def __beat_to_list( self , file_path , regex_pattern ) -> list:

        with open( file_path , 'r' ) as file:

            file_string = file.read()

            # filter beat value
            result_iter =  re.finditer( regex_pattern , file_string )

            # to list
            beats_list = []

            for match in result_iter :
                
                temp_string = match.group()

                # string to float
                beats_list.append( float( temp_string ) )


        #
        return beats_list
        
    def average( self , numpy_array , number ):
        
        return numpy_array / number

    def file_tempo( self , estimated_file_path , reference_file_path ):
    
        #
        with open( reference_file_path , 'r' ) as file:

            temp_value = file.read()

        # to float
        reference_tempo = float( temp_value )


        # multithreading 
        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            # execute task
            future_autocorrelation = executor.submit( self.__autocorrelation_method , reference_tempo , estimated_file_path )
            future_fourier = executor.submit( self.__fourier_method , reference_tempo , estimated_file_path )
            

            # get result
            autocorrelation_result = future_autocorrelation.result()
            fourier_result = future_fourier.result()
            

        # create template
        result_dict = { 'autocorrelation': None, 'fourier': None }
        
        # calculate score
        result_dict['autocorrelation'] = autocorrelation_result
        result_dict['fourier'] = fourier_result
        

        # return score
        return result_dict

    def file_beat( self , estimated_file_path , reference_file_path , regex_pattern ):
        
        # multithreading 
        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            # execute task
            future_reference_list = executor.submit( self.__beat_to_list , reference_file_path , regex_pattern )
            future_estimated_list = executor.submit( self.__beats_method , estimated_file_path )
            

            # get result
            reference_list_result = future_reference_list.result()
            estimated_list_result = future_estimated_list.result()


        # calculate score
        score = mir_eval.beat.p_score( numpy.asarray( reference_list_result ) , estimated_list_result )


        # return score
        return score

    def folder_tempo( self , folder_path ):
        
        path_cls = path.Path( folder_path )

        reference_file_list = path_cls.get_file_list( "annotation" )
        estimated_file_list = path_cls.get_file_list( "wav" )


        temp_array = numpy.zeros(4)

        # multiprocessing  
        with concurrent.futures.ProcessPoolExecutor( max_workers=5 ) as executor:
            
            future_list = []

            # execute task
            for estimated_file , reference_file in zip( estimated_file_list , reference_file_list ) :
                
                # file( estimated_file , reference_file )
                future = executor.submit( self.file_tempo , estimated_file , reference_file )
                
                future_list.append( future )


            # Progress bar 
            with tqdm.tqdm( total=len( estimated_file_list ) ) as pbar:
                
                # get result
                for future in concurrent.futures.as_completed( future_list ) :

                    temp_list = self.__dict_to_list( future.result() )

                    temp_array += temp_list 


                    # update progress bar
                    pbar.update( 1 )
        

        # get average
        result_array = self.average( temp_array , len( estimated_file_list ) )

        result_dict = self.__array_to_dict( result_array )
        
    
        #
        return result_dict

    def folder_beat( self , folder_path , regex_pattern ):
        
        path_cls = path.Path( folder_path )

        reference_file_list = path_cls.get_file_list( "annotation" )
        estimated_file_list = path_cls.get_file_list( "wav" )

        temp_float = 0.0

        # multiprocessing  
        with concurrent.futures.ProcessPoolExecutor() as executor:
            
            future_list = []

            # execute task
            for estimated_file , reference_file in zip( estimated_file_list , reference_file_list ) :
                
                # file( estimated_file , reference_file )
                future = executor.submit( self.file_beat , estimated_file , reference_file , regex_pattern )
                
                future_list.append( future )


            # Progress bar 
            with tqdm.tqdm( total=len( estimated_file_list ) ) as pbar:
                
                # get result
                for future in concurrent.futures.as_completed( future_list ) :

                    temp_float += future.result()


                    # update progress bar
                    pbar.update( 1 )
        

        # get average score
        score_average = temp_float / len( estimated_file_list )
        
    
        #
        return score_average