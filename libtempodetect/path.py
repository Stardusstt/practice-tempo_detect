import pathlib



class Path:

    def __init__( self , root_path ):

        # init path
        self.root_path = pathlib.Path( root_path )
        
    def get_file_list( self , child_name ):

        # get child path
        child_path = self.root_path / child_name
        
        # whether the path is existing 
        if child_path.exists() == False :
             
            print( child_path )
            raise OSError("Directory does not exist.")

        #
        # get file list
        file_list = []

        # get typepath
        for temp_typepath in child_path.iterdir() :

            file_list.append( temp_typepath )

        
        #
        return file_list    

       

    

            
    
        