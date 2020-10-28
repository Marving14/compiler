import basic

while True: 
    text = input('command > ')
    result, error = basic.run('<stdin>', text)
    
    if error: print(error.as_string())
    else: print(result)
 




#https://www.youtube.com/watch?v=3PW552YHwy0&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD&index=5&ab_channel=CodePulse
