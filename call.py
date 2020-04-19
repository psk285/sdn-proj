import urllib, os
j = 1
while j <= 5:
	i = 1
	while i <= 2:
    		os.system('wget http://10.0.0.1/files/fshared_%s.file'%i)
    	i = i + 1
	os.system('rm fshared_*')
	j = j + 1