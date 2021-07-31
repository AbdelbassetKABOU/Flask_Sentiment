

import pandas as pd
import numpy as np

creds = pd.read_csv('credentials.csv')

#creds.head()
#	username 	password 	v1 	v2
#0 	Quinlan 	5210 	         0 	1
#1 	Davis 	        5783 	         0      0
#2 	Montana 	3134             0 	0
#3 	Quintessa 	8790 	         0 	1
#4 	Camden 	        4837 	         0 	0



#def authenticate_user(username)

def get_creds(username, password):
    line = creds[creds.username==username]
    #print (line.password)
    if len(line.password) != 0 :
        if line['password'].item() == int(password) :
            print ('OK')    
            print ('====>', line['v1'], line['v2'])
            #return (line['v1'][0], line['v2'][0])
            return (int(line['v1']), int(line['v2']))
    return (None, None)
