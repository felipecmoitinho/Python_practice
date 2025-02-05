# Building some functions

# Exercise 3.11.3
def triangle(x, y):
    for i in range(y):
        print(x*(i+1))

# Exercise 3.11.4
def rectange(x,y,z):
    for i in range(z):
        print(x*y)

if 0 < x:
    if x < 10:
        print('X is a single digit number')

def factorial(n):
    if n == 0:
        return 1
    else:
        recurse = factorial(n-1)
        return n * recurse

def se_letras(word, letters):
    for letra in letters:
        if letra in word:
            return True
        else:
            return False



