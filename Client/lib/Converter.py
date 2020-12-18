n = 4
def Encode(txt):
    txt = " " + str(txt)
    intvalue = 0
    for x in txt:
        intvalue = intvalue*pow(10,n) + ord(x)
    return intvalue

def Decode(number):
    zeros = (n - len(str(number))%n)%n
    number= zeros*"0" +str(number)
    result=""
    for x in range(int(len(number[1:])/n)+1):
        index = x*n
        result += chr(int(number[index:index+n]))
    return result







