# Script to generate different possible paths depending upon the latency of the n/w

'''
Terminology used:

1->2 : It tells that the path is from 1 to 2

1->2->3 : It tells that the path is from 1 to 3 via 2

link_1_2 : It gives the ping time between hosts 1 and 2. 

'''


f = open('ping_stat_2_3','r')
link_2_3 = f.readline()
f.close()
f = open('ping_stat_1_3','r')
link_1_3 = f.readline()
f.close()
f = open('ping_stat_1_2','r')
link_1_2 = f.readline()
f.close()

# pathcongested shows that path between two switches is congested and we should go for an alternative path. 
pathcongested = 'none'  
# Path congested 1->2 and 2->1
path1 = link_1_2
path2 = link_1_3+link_2_3

min1=min(path1,path2)
if(min1 == path1):
	print "There is no congestion between switches 1 and 2. Hence we can directly go from switch 1 to 2 and switch 2 to 1"
	print "1->2->2"
	print "2->1->1"
elif(min1 == path2):
	print "There is congestion between switches 1 and 2. Hence we need to go from switch 1 to 2 via 3 and switch 2 to 1 via 3"	
	pathcongested ='1:2' 
	print "1->3->2"
	print "2->3->1"	
print ""	
# Path congested 1->3 and 3->1
path1 = link_1_3
path2 = link_1_2+link_2_3

if(pathcongested!='none'):
	print "There is no congestion between switches 1 and 3. Hence we can directly go from switch 1 to 3 and from switch 3 to 1"
	print "1->3->3"
	print "3->1->1"
else:		
	min1=min(path1,path2)
	if(min1 == path1 ):
		print "There is no congestion between switches 1 and 3. Hence we can directly go from switch 1 to 3 and switch 3 to 1"
		print "1->3->3"
		print "3->1->1"
	elif(min1 == path2):
		print "There is congestion between switches 1 and 3. Hence we need to go from switch 1 to 3 via 2 and switch 3 to 1 via 2"
		pathcongested ='1:3'
		print "1->2->3"
		print "3->2->1"
print ""
# Path congested 3->2 and 2->3
path1 = link_2_3
path2 = link_1_3+link_1_2

if(pathcongested!='none'):
	print "There is no congestion between switches 2 and 3. Hence we can  directly go from switch 2 to 3 and from switch 3 to 2"
	print "3->2->2"
	print "2->3->3"
else:			
	min1=min(path1,path2)
	if(min1 == path1):
		print "There is no congestion between switches 2 and 3. Hence 	we can directly go from switch 2 to 3 and from switch 3 to 2"
		print "3->2->2"
		print "2->3->3"
	elif(min1 == path2):
		print "There is congestion between switches 2 and 3. Hence we 	need to go from switch 3 to 2 via 1 and from switch 2 to 3 via 1"
		pathcongested ='3:2'
		print "3->1->2"
		print "2->1->3"
		
