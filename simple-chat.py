import gradio as gr
import openai
import os
import json
import glob

openai.api_key = ""
messages = []
savepath = "output/output.txt"
save_dir = "output"

def clearChat():
    messages.clear()
    return None
    
def load_save_file(value):
    test = []
    with open(value, 'r') as file:
        json_data = json.load(file)
    
    messages.clear()
    system = ""
    filename = save_directory = os.path.basename(value)
    for data in json_data:
        messages.append({"role": data["role"], "content": data["content"]})
        if (data["role"] == "system"):
            system = data["content"]

    return [format_message_data(), system, filename, None]

def getSaveFiles():
    files = glob.glob(save_dir + '/' + "*.txt")
    file_names = []
    for file in files:
        file_names.append(file)
    return file_names

def format_message_data():
    chat_history = ""
    for message in messages[0:]:
        if message["role"] != "system":
            chat_history += message["role"] + ": " + message["content"].lstrip('\n') + "\n\n"
    return chat_history

def chat(Context, Content, file_name, autosave):
    if Context:
        if len(messages) > 0 and messages[0]["role"] == "system":
            messages[0]["content"] = Context
        else:
            messages.insert(0, {"role": "system", "content": Context})
    
    messages.append({"role": "user", "content": Content})

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    
    #add the openai response to the memory
    messages.append(response['choices'][0]['message'])
    
    if autosave:
        # Extract the directory path from the full path and filename
        save_directory = os.path.dirname(savepath)
        
        #Check to make sure the directory exists
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        #Save the messages to file
        with open(savepath, 'w') as f:
            f.write(json.dumps(messages))
    
    return format_message_data()
    
with gr.Blocks() as demo:
    output = gr.Textbox(label="Output Box", lines=30, value=format_message_data)
    with gr.Row():
        clear = gr.Button("New Chat")
        file_dropdown = gr.Dropdown(getSaveFiles(), label="Load File")
        file_name = gr.Textbox(label="Save file name")
        autosave = gr.Checkbox(label="Autosave")
    
    Context = gr.Textbox(lines=1, placeholder="Enter information to instruct how inputs stuff...")
    Content = gr.Textbox(lines=5, placeholder="Text...")
    submit = gr.Button("Submit")
    submit.click(fn=chat, inputs=[Context, Content, file_name, autosave], outputs = output)
    clear.click(fn=clearChat,inputs=None, outputs = output)
    file_dropdown.change(fn=load_save_file, inputs=file_dropdown, outputs=[output, Context, file_name, file_dropdown])

demo.launch()