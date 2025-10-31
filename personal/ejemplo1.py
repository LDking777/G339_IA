print("Hola mundo") 

a = 24 
b = 25 

c = a * b 
print(c) 

for i in range(5): 
  print(f"hola") 

count = 4
while count>0: 
  print(count)
  count = count - 1 
  if(count == 0):
   print(f"Empiezaaa!!!") 

class Perro:
    def __init__(self, nombre):
        self.nombre = nombre 
mi_perro = Perro("firulais") 

print(mi_perro.nombre)


name = input("ingresa tu nombre: ")
print(name)  
print(len(name)) 

mi_perro2 = Perro("Vegito") 
print(mi_perro.nombre)