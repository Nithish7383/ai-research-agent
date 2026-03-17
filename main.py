from agent import agent

print("🔎 AI Research Agent")
print("Type 'exit' to quit\n")

while True:
    query = input("Ask something: ")

    if query.lower() == "exit":
        break

    response = agent.run(query)

    print("\n🤖 Answer:\n")
    print(response)
    print("\n----------------------\n")