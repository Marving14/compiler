import os


cmd = 'python shell.py'

returned = os.system(cmd)
example = 'RUN("test1.marving")'
returned2 = os.system(cmd)

print(returned)
print(returned2)


