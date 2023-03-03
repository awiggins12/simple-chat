import gradio as gr
import openai
import os
import json
import glob
import datetime

openai.api_key = ""
messages = []
savepath = "output/output.txt"
save_dir = "output"

"""
TODO
* Auto-clear the submit box?  
* Better placeholder text and labels for the system/content
* Improve UI
* Convert the output to html?  Then convert markdown to html
* Edit Response
* Save re-generated responses
* Scroll to end of output
*  Improve error handling of files
"""


def clearChat():
    messages.clear()
    return [None, get_new_filename()]
    
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

def regenerate_response(context, content, file_name, autosave, autoclear):
    #if the last element in the array is assistant, remove it.
    if len(messages) > 0 and messages[-1]["role"] == "assistant":
        messages.pop()
        #now check to see if the next to last message is from user, we want to remove that now.
        if len(messages) > 0 and messages[-1]["role"] == "user":
            messages.pop()
    return chat(context, content, file_name, autosave, autoclear)

def format_message_data():
    chat_history = ""
    for message in messages[0:]:
        if message["role"] != "system":
            chat_history += message["role"] + ": " + message["content"].lstrip('\n') + "\n\n"
    return chat_history
    
def get_new_filename():
    now = datetime.datetime.now()
    formatted_time = now.strftime("%H%M%S")
    return formatted_time + "_Default.txt"

def chat(context, content, file_name, autosave, autoclear):
    if context:
        if len(messages) > 0 and messages[0]["role"] == "system":
            messages[0]["content"] = context
        else:
            messages.insert(0, {"role": "system", "content": context})
    
    messages.append({"role": "user", "content": content})

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    
    #add the openai response to the memory
    messages.append(response['choices'][0]['message'])
    
    if autosave:
        
        #Check to make sure the directory exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        #Save the messages to file
        with open(save_dir + '/' + file_name, 'w') as f:
            f.write(json.dumps(messages))
    
    if autoclear:
            content = ""
    
    return [format_message_data(), content]
    
with gr.Blocks() as demo:
    output = gr.Textbox(label="Output Box", value=format_message_data)
    with gr.Row(variant="panel").style(equal_height=False):
        with gr.Column(scale=1):
            clear = gr.Button("New Chat")
        with gr.Column(scale=2):
            file_dropdown = gr.Dropdown(getSaveFiles(), label="Load File")
        with gr.Column(scale=2):            
            file_name = gr.Textbox(label="Save file name", value=get_new_filename)
        with gr.Column(scale=1):
            autosave = gr.Checkbox(label="Autosave", value=True)
            autoclear = gr.Checkbox( label="Auto-clear input", value=True)
    
    context = gr.Textbox(lines=1, placeholder="Enter information to instruct how inputs stuff...")
    content = gr.Textbox(lines=5, placeholder="Text...")
    with gr.Row(variant="panel"):
        with gr.Column(scale=30):
            submit = gr.Button("Submit", variant='primary')
        with gr.Column(scale=1):
            regenerate = gr.Button(value="regen")
    submit.click(fn=chat, inputs=[context, content, file_name, autosave, autoclear], outputs = [output, content])
    regenerate.click(fn=regenerate_response, inputs=[context, content, file_name, autosave, autoclear], outputs = [output, content])
    clear.click(fn=clearChat,inputs=None, outputs = [output, file_name], show_progress=False)
    file_dropdown.change(fn=load_save_file, inputs=file_dropdown, outputs=[output, context, file_name, file_dropdown])

demo.launch()