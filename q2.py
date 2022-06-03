from libtempodetect import report
from libtempodetect import path

import pathlib



def all( root_path ):
    
    root_path = pathlib.Path( root_path )

    for temp_typepath in root_path.iterdir() :

        print( temp_typepath.stem )


        report_cls = report.Report()

        result = report_cls.folder( temp_typepath )
        print( result )


if __name__ == '__main__':


    # Ballroom
    folder_path = R"D:\Temporary\ttttt\MIR_HW2_Dataset\Ballroom\ALL"
    regex_pattern = R"\d\S+"

    report_cls = report.Report()

    
    result = report_cls.folder_beat( folder_path , regex_pattern )
    print( "Ballroom : " , result )


    # # SMC
    # folder_path = R"D:\Temporary\ttttt\MIR_HW2_Dataset\SMC"
    # regex_pattern = R"\d\S+"

    # report_cls = report.Report()

    
    # result = report_cls.folder_beat( folder_path , regex_pattern )
    # print( "SMC : " , result )


    # # JCS
    # folder_path = R"D:\Temporary\ttttt\MIR_HW2_Dataset\JCS"
    # regex_pattern = R"\d\S+"

    # report_cls = report.Report()

    
    # result = report_cls.folder_beat( folder_path , regex_pattern )
    # print( "JCS : " , result )

    
    # # ASAP
    # folder_path = R"D:\Temporary\ttttt\MIR_HW2_Dataset\ASAP"
    # regex_pattern = R"\d\S+(?=\t\d)"

    # report_cls = report.Report()

    
    # result = report_cls.folder_beat( folder_path , regex_pattern )
    # print( "ASAP : " , result )


    


