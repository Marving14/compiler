import basic

while True: 
    text = input('command > ')
    result, error = basic.run('<stdin>', text)
    
    if error: print(error.as_string())
    elif result: print(result)
 




#https://www.youtube.com/watch?v=acCfcPXiX3A&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD&index=8&ab_channel=CodePulse
