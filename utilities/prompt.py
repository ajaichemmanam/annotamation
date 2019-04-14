def promptInput(message):
    cont = input(message + " Enter y / n ")
    while cont.lower() not in ("y", "n"):
        cont = input("Enter y for yes and n for no. " + message)
    if cont == "n":
        return False
    elif cont == "y":
        return True
