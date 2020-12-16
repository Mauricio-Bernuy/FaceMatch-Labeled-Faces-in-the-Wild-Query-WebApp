import functions

for i in [-1]:#100,200,400,800,1600,3200,6400,12800,-1]:
    functions.generate_encodings(i)
    functions.write_encodings(i)
    functions.clear_files()