def promptInput(message):
    cont = input(message + " Enter y / n " + "\n")
    while cont.lower() not in ("y", "n"):
        cont = input("Enter y for yes and n for no. " + message + "\n")
    if cont == "n":
        return False
    elif cont == "y":
        return True


def promptInt(message):
    isSuccess = False
    val = 0
    while (not isSuccess):
        userInput = input(message + "\n")
        try:
            val = int(userInput)
            isSuccess = True
        except ValueError:
            print("Please Enter a valid Integer. ")
            isSuccess = False
    return val


def promptRatio(message):
    isSuccess = False
    val1 = val2 = 0
    while (not isSuccess):
        userInput = input(message + (" Eg: 10:90") + "\n")
        try:
            text = userInput.split(':')
            val1 = int(text[0])
            val2 = int(text[1])
            if(val1+val2 == 100):
                isSuccess = True
            else:
                print("Ratio should add upto 100")
                isSuccess = False
        except ValueError:
            print("Please Enter a valid Ratio. ")
            isSuccess = False
        except Exception as e:
            print(str(e))
    return val1, val2
