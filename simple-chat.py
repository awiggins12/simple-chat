import gradio as gr
import openai
import os
import json
import glob
import datetime
import markdown

openai.api_key = "PUT KEY HERE"
messages = []
savepath = "output/output.txt"
save_dir = "output"

"""
TODO
* Edit Response
* Save re-generated responses
* Order files by most recent
* Truncate messages if they exceed 4000 tokens
"""

def clear_chat():
    messages.clear()
    return [format_message_data(), get_new_filename()]

# I added system and file_name as inputs because when this is firing multiple times the 
# second time has empty information and if I pass that info in then I can just ignore the other firing
def load_save_file(value, system, file_name):
 
    if (value is not None and len(value) > 0):
        messages.clear()
    
        selected_value = value[0] if isinstance(value, list) else value
        
        with open(selected_value, 'r') as file:
            json_data = json.load(file)

        file_name = save_directory = os.path.basename(selected_value)
        for data in json_data:
            messages.append({"role": data["role"], "content": data["content"]})
            if (data["role"] == "system"):
                system = data["content"]

    return [format_message_data(), system, file_name, None]

def get_save_files():
    files = glob.glob(save_dir + '/' + "*.txt")
    file_names = []
    for file in files:
        file_names.append(file)
    return file_names

def regenerate_response(context, content, file_name, autosave, autoclear):
    #if the last element in the array is assistant, remove it.
    if len(messages) > 0 and messages[-1]["role"] == "assistant":
        messages.pop()

    return chat(context, "", file_name, autosave, autoclear)

def format_message_data():
    chat_history = "<div class='chat_container'>"
    for message in messages[0:]:
        if message["role"] != "system":
            chat_history += "<div class='{}'>{}</div>".format(message["role"],markdown.markdown(message["content"], output_format='html5'))
    chat_history += "</div>"
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
    
    if len(content) > 0:
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
        
        if len(file_name) == 0:
            file_name = get_new_filename()
        
        #Save the messages to file
        with open(save_dir + '/' + file_name, 'w') as f:
            f.write(json.dumps(messages))
    
    if autoclear:
            content = ""
    
    return [format_message_data(), content, get_save_files()]


css = "div.user {background-color:rgba(236,236,241,var(--tw-text-opacity)); text-align:right; }"
css += "div.assistant {background-color: rgba(68,70,84,var(--tw-bg-opacity)); color: rgba(236,236,241,var(--tw-text-opacity));}"
css += ".user,.assistant {padding: 15px 10px 15px 10px; margin:15px; border-radius: 5px;}"
css += "code {background-color: black; color: white; margin: 15px 10px 15px 10px; padding: 10px; display: inline-block;}"
css += ".chat_container {background-color:rgb(249 250 251 / var(--tw-bg-opacity)); padding: 5px; border-radius: 3px; min-height:100px; font-size:1.2rem;}"
css += ".dark .chat_container {background-color:rgb(17 24 39 / var(--tw-bg-opacity));}" 
css += ".dark .user {background-color:#66666d; color: rgb(229 231 235 / var(--tw-text-opacity));}"

with gr.Blocks(css=css, title="Simple Chat") as demo: 
    output = gr.HTML(value=format_message_data)
    with gr.Row(variant="panel").style(equal_height=False):
        with gr.Column(scale=1):
            clear = gr.Button("New Chat")
        with gr.Column(scale=2):
            file_dropdown = gr.Dropdown(get_save_files(), label="Load File")
        with gr.Column(scale=2):            
            file_name = gr.Textbox(label="Save file name", value=get_new_filename)
        with gr.Column(scale=1):
            autosave = gr.Checkbox(label="Autosave", value=True)
            autoclear = gr.Checkbox( label="Auto-clear input", value=True)
    
    context = gr.Textbox(label="Assistant Behavior", lines=1, placeholder="Set the behavior of the assistant (this gives weak results compared to message)...")
    content = gr.Textbox(label="Message", lines=5)
    with gr.Row(variant="panel"):
        with gr.Column(scale=30):
            submit = gr.Button("Submit", variant='primary')
        with gr.Column(scale=1):
            regenerate = gr.Button(value="Regenerate")
    
    #Bindings
    submit.click(fn=chat, inputs=[context, content, file_name, autosave, autoclear], outputs = [output, content, file_dropdown])
    regenerate.click(fn=regenerate_response, inputs=[context, content, file_name, autosave, autoclear], outputs = [output, content, file_dropdown])
    clear.click(fn=clear_chat,inputs=None, outputs = [output, file_name], show_progress=False)
    file_dropdown.change(fn=load_save_file, inputs=[file_dropdown, context, file_name], outputs=[output, context, file_name, file_dropdown])
demo.launch(inbrowser=True)