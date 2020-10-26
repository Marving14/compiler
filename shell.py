import basic

while True: 
    text = input('command > ')
    result, error = basic.run(text)
    
    if error: print(error.as_string())
    else: print(result)
    

