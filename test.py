f = open("testing.txt","w")
for i in range(0,100000000):
	f.write(str(i))
f.close()
