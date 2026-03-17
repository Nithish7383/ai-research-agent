from ddgs import DDGS

def search_web(query: str):
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=5):
            results.append(f"{r['title']} - {r['body']}")

    return "\n".join(results)   