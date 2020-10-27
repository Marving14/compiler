import basic

while True: 
    text = input('command > ')
    result, error = basic.run('<stdin>', text)
    
    if error: print(error.as_string())
    else: print(result)
    




#https://www.youtube.com/watch?v=-ic5381rYcg&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD&index=4&ab_channel=CodePulse
