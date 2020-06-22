import time
from random import Random
import copy
import generate_card_number

def greetings():
	print("**************************************")
	print("|     Welcome to our digital bank    |")
	print("**************************************")
	print()
	print("In order to create your account you need to provide us some data.")
	print()
	name=input("Full Name: ")
	phone_number=input("Phone Number: ")
	print()
	pin=input("Insert your secret pin: ")
	print()
	print("Creating account...")
	time.sleep(10)
	print("Account successfully created!")
	print()
	print()
	card_number=generate_card_number.number_generator()[0].split('.')[0]
	#print("Your card number is: " + card_number)

	with open("accounts.txt", "a") as file:
		account=name+"\n"+phone_number+"\n"+str(card_number)+" "+pin+"\n"
		file.write(account)



