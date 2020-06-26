# Digital Bank   :bank: :credit_card:

## What it is?

With this digital bank you have a way to access your bank remotely and more securely.
Our main focus on this project was to understand how we could verify the PIN of the bank users.

## How it works?

We assume that you have already registered in the physical bank, and have a real card.
For demo purposes we have created a function to create a new bank account.

### Server 

First we need to run the server, in order to communicate with the ATM. The server here will work as the digital bank servers.

    $ python app.py server
    
If it is needed to create a new account just run:
    
    $ python app.py server gen

### Client

The Client here will act as an ATM. 

    $ python app.py client
