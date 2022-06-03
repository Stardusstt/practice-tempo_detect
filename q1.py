from libtempodetect import report
from libtempodetect import path

import pathlib



def all( root_path ):
    
    root_path = pathlib.Path( root_path )

    for temp_typepath in root_path.iterdir() :

        print( temp_typepath.stem )


        report_cls = report.Report()
        
        result = report_cls.folder_tempo( temp_typepath )
        print( result )


if __name__ == '__main__':

    # folder_path = R"D:\Temporary\ttttt\MIR_HW2_Dataset\Ballroom\ALL"

    # report_cls = report.Report()
    
    # result = report_cls.folder_tempo( folder_path )
    # print( result )
    
    
    ISMIR2004_path = R"D:\Temporary\ttttt\MIR_HW2_Dataset\ISMIR2004"
    
    all( ISMIR2004_path )


