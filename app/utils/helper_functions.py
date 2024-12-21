# Utility functions like chunk_text, build_prompt, etc.
from IPython.display import Image, display
#from app.services.LLM_service import GraphBuilder 

def Visualize_Graph():
    print("in")
    Graph = GraphBuilder()
    print(Graph.get_graph().draw_mermaid())



def build_prompt(query, context_chunks):
    prompt_start = (
        "Answer the question based on the context below. If you don't know the answer based on the context provided below, just respond with 'I don't know' instead of making up an answer. Don't start your response with the word 'Answer:'"
        "Context:\n"
    )
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    prompt = ""
    # append contexts until hitting limit
    for i in range(1, len(context_chunks)):
        if len("\n\n---\n\n".join(context_chunks[:i])) >= PROMPT_LIMIT:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(context_chunks[:i-1]) +
                prompt_end
            )
            break
        elif i == len(context_chunks)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(context_chunks) +
                prompt_end
            )
    return prompt   

def construct_messages_list(chat_history, prompt):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    # Populate the messages array with the current chat history
    for message in chat_history:
        if message['isBot']:
            messages.append({"role": "system", "content": message["text"]})
        else:
            messages.append({"role": "user", "content": message["text"]})

    # Replace last message with the full prompt
    messages[-1]["content"] = prompt    
    
    return messages