import basic

while True: 
    text = input('command > ')
    if text.strip() =="": continue
    result, error = basic.run('<stdin>', text)
    
    if error: print(error.as_string())
    elif result: 
        if len(result.elements) ==1:
            print(repr(result.elements[0]))
        else :
            print(result)
 




#https://www.youtube.com/watch?v=zKCckdwwBsU&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD&index=13&ab_channel=CodePulse

