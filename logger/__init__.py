import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    , filename='app.log', filemode='w', datefmt='%d-%b-%y %H:%M:%S')
