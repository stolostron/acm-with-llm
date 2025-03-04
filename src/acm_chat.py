
import sys
from acm_agents import process
if len(sys.argv) <1 :
        print("Usage: python acm_chat.py <question that you want it to answer>")
        sys.exit(1)

print(sys.argv[1])
value = process(sys.argv[1])
print(value)