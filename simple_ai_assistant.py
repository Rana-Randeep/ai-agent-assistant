#standard library imports
import os
from types import SimpleNamespace

#Third-party imports
from openai import OpenAI
from dotenv import load_dotenv

#Local modules
from Utilities.utilities import log
from tools import TOOLS, run_tool


load_dotenv() #by default looks for .env file


client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages=[]

# Safety limit : the max number of model rounds for one user question
MAX_STEPS = 5

messages.append(
    {
        "role":"system",
        "content":"You are helpful, humble assistant."
        "Answer general questions (programming, science, advice) from your own knowledge. "
        "Use a tool ONLY when the user asks for the current time, the weather or their city. "
        "Keep answers under 100 words and do not print count of words."
    }
    
)

def stream_chat(history):
    stream = client.chat.completions.create(
        model = os.getenv("MODEL"),
        messages = history,
        tools = TOOLS,
        stream = True,
    )
    
    full_response = ""
    calls={}
    label_printed = False

    #Streaming Started
    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            #1. Content Streaming : Do we have message (content) from the LLM
            if delta.content:
                if not label_printed:
                    print("Assistant: ", end="", flush=True)
                    label_printed = True

                print (delta.content, end = "", flush=True)
                full_response += delta.content

            #2. Tool Calls
            for tc in (delta.tool_calls or []) :
                obj = calls.setdefault(
                    tc.index,
                    SimpleNamespace(id=None, function=SimpleNamespace(name="", arguments="")),
                )
                if tc.id:
                    obj.id = tc.id
                if tc.function and tc.function.name:
                    obj.function.name += tc.function.name
                if tc.function and tc.function.arguments:
                    obj.function.arguments += tc.function.arguments

    except KeyboardInterrupt:
        print("\n [Stopped by you]")
        calls = {}

    if label_printed:
        print() #Move to the next line after the assistant response

    calls_list = []
    for key in sorted(calls):        # converting dictionary into list
        calls_list.append(calls[key])

    return full_response, calls_list


def build_tool_calls_payload(tool_calls):
    """
    Converts our collected tool calls into the dict format
    that the API expects inside an assistant message.
    """

    payload = []
    for tool_call in tool_calls:
        tool_call_dict = {
            "id" : tool_call.id,
            "type" : "function",
            "function" : {
                "name" : tool_call.function.name,
                "arguments" : tool_call.function.arguments,
            },
        }
        payload.append(tool_call_dict)

    return payload

# Chat loop starts from here
while True:

    user_input = input("\nRana: ")

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    messages.append(
        {
            "role":"user",
            "content":user_input
        }
    )

    #Chained Tool Calling
    for step in range(MAX_STEPS):

        # response = client.chat.completions.create(
        #     model=os.getenv("MODEL"),
        #     messages=messages,
        #     tools = TOOLS
        # )
        full_response, tool_calls = stream_chat(messages)
        
        #msg = response.choices[0].message

        if not tool_calls:
            break

        log(f"Step {step + 1}: model requested {len(tool_calls)} tool calls")
        
        messages.append({
            "role" : "assistant",
            "content" : full_response,
            "tool_calls" : build_tool_calls_payload(tool_calls)
        })

        for tool_call in tool_calls:
            result = run_tool(tool_call)

            messages.append({
                "role" : "tool",
                "tool_call_id" : tool_call.id,
                "content" : str(result),
            })

    else :    
        # Ran out of steps: The model never gave the final answer
        fallback = "Sorry, I could not finish this within the step limit."
        messages.append({
            "role":"assistant",
            "content": fallback
        })
        print(" :) Assistant: " + fallback)
        continue

    # messages.append({                  Already done in stream_chat() function. therefore commented here
    #     "role" : "assistant",
    #     "content" : msg.content
    # })

    # print("Assistant: " + (msg.content or""))    Already done in stream_chat() function. therefore commented here
    