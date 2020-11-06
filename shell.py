import basic

while True: 
    text = input('marving > ')
    if text.strip() =="": continue
    result, error = basic.run('<stdin>', text)
    
    if error: print(error.as_string())
    elif result: 
        if len(result.elements) ==1:
            print(repr(result.elements[0]))
        else :
            print(repr(result))
 




#https://www.youtube.com/watch?v=-7a0ys7gF5E&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD&index=15&ab_channel=CodePulse


#https://github.com/davidcallanan/py-myopl-code

