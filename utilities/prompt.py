def promptInput(message):
    cont = input(message + " Enter y / n ")
    while cont.lower() not in ("y", "n"):
        cont = input("Enter y for yes and n for no. " + message)
    if cont == "n":
        return False
    elif cont == "y":
        return True


def promptInt(message):
    isSuccess = False
    val = 0
    while (not isSuccess):
        userInput = input(message)
        try:
            val = int(userInput)
            isSuccess = True
        except ValueError:
            print("Please Enter a valid Integer. ")
            isSuccess = False
    return val
