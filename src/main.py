from src.agent import agent_executor

print("🔎 AI Research Agent")
print("Type 'exit' to quit\n")

while True:
    query = input("Ask something: ")

    if query.lower() == "exit":
        print("👋 Goodbye!")
        break

    try:
        result = agent_executor.invoke({
            "input": query,
            "chat_history": agent_executor.memory.buffer if hasattr(agent_executor.memory, "buffer") else "",
        })

        response = result.get("output", "No response generated.")
        intermediate_steps = result.get("intermediate_steps", [])

        # Show agent reasoning in terminal
        if intermediate_steps:
            print("\n🧠 Agent Reasoning:")
            for i, (action, observation) in enumerate(intermediate_steps, 1):
                print(f"  Step {i} → Tool: {action.tool}")
                print(f"  Query: {action.tool_input}")
                print(f"  Result: {str(observation)[:300]}...")
                print()

        print("\n🤖 Answer:\n")
        print(response)
        print("\n----------------------\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        print("----------------------\n")