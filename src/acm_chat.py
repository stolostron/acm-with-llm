
import sys
from acm_agents import process

def respond(response):
    """
    Display a streaming response from a generator without line breaks between parts.
    This is a hack and there is a better way to do it
    
    Args:
        response_generator: A generator that yields parts of the response
    """
    for part in response:
        sys.stdout.write(part)
        sys.stdout.flush()  # Ensure output is displayed immediately


def help():
    print("These are some of the things I can do today. This will evolve over time \n")
    print("1. Create an ACM GRC Policy. So you can ask me:")
    print("     Create a ACM policy to create a namespace called lightspeed")
    print("2. Or ask a question that can be answered about resources in the fleet that ACM Manages.")
    print("As of now, I can only answer from data that is in ACM Search - but that will change soon")
    print("So you can ask me:")
    print("     How many policies are there in the current ACM installation")
    print("     How many alert-manager pods are running")
    print("     How many pods are not running or completed")


def main():
    print("=======================================================")
    print("Welcome to the world of the interactive ACM Agent!")
    print("Type 'help' to see the commands that you can run today")
    print("Type 'quit' to exit")
    print("=======================================================")
        
    while True:
        # Display prompt and wait for input
        user_input = input("\n> ")

        if user_input.lower() == "quit":
            print("Goodbye - Hope to see you again!")
            break
        if user_input.lower() == "help":
            help()
            continue  
        
        response = process(user_input.lower())

        print("return class: ",type(response))
            
        # Handle the response based on its type
        # this is a hack
        if hasattr(response, '__iter__') and not isinstance(response, (str, bytes)):
            # It's a generator (streaming response)
            respond(response)
        else:
            print(response)

if __name__ == "__main__":
    main()            
