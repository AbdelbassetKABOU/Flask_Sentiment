

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

def get_creds(username, password):
    line = creds[creds.username==username]
    if len(line.password) != 0 :
        if line['password'].item() == int(password) :
            return (int(line['v1']), int(line['v2']))
    return (None, None)
