import gradio as gr
import openai
import os
import json
import glob
import datetime
import markdown
from dotenv import load_dotenv

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

def is_api_key_set():
    api_key_set = False
    if os.path.isfile('.env'):
        load_dotenv()
        if os.environ.get('API_KEY') is not None:
            api_key_set = True
    return api_key_set

def set_new_api_key(api_key):
    #Write the api key to the .env file
    with open('.env', 'w') as f:
        f.write(f'API_KEY={api_key}')
        
    #load the key
    load_dotenv()
    set_api_key()
    #demo.launch(inbrowser=False)
    return gr.update(visible=False);

def hide():
    return gr.update(visible=False);
    
def show():
    return gr.update(visible=True);

def set_api_key():
    openai.api_key = os.environ.get('API_KEY')
    api_key_set = True
    return None;
    
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

def get_models():
    return ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-32k']

def regenerate_response(context, content, file_name, autosave, autoclear, max_length, temperature, top_p, frequency_penalty, presence_penalty, historyLength, model):
    #if the last element in the array is assistant, remove it.
    if len(messages) > 0 and messages[-1]["role"] == "assistant":
        messages.pop()

    return chat(context, "", file_name, autosave, autoclear, max_length, temperature, top_p, frequency_penalty, presence_penalty, historyLength, model)

def format_message_data():
    
    chat_history = "<div class='chat_container'>"
    for index, message in enumerate(messages):
        if message["role"] != "system":
            onclick = "var gradio = document.getElementsByTagName(\"gradio-app\")[0].shadowRoot; var textBox = gradio.querySelector(\"#update_content textarea\"); var inputBox = gradio.querySelector(\"#array_number input\"); var div = gradio.getElementById(\"array_{}\"); inputBox.value = {}; textBox.value = div.textContent || div.innerText || \"\"; const input_event = new Event(\"input\"); inputBox.dispatchEvent(input_event); textBox.dispatchEvent(input_event);".format(index, index)
            chat_history += "<div id=\"array_{}\" onclick='{}' class='chat_text {}'>{}</div>".format(index, onclick, message["role"],markdown.markdown(message["content"], output_format='html5'))
    chat_history += "</div>"
    return chat_history

 

def get_new_filename():
    now = datetime.datetime.now()
    formatted_time = now.strftime("%H%M%S")
    return formatted_time + "_Default.txt"

def chat(context, content, file_name, autosave, autoclear, max_length, temperature, top_p, frequency_penalty, presence_penalty, historyLength, model):

    payload = []

    # strip out the system message if it is present
    for message in messages:
        if message['role'] != 'system':
            payload.append(message)

    if historyLength > len(payload):
        historyLength = len(payload)
    payload = payload[-historyLength:]

    if context:
        # only send 'system' message if currently populated
        payload.insert(0, {"role": "system", "content": context})

        if len(messages) > 0 and messages[0]["role"] == "system":
            messages[0]["content"] = context
        else:
            messages.insert(0, {"role": "system", "content": context})
    
    if len(content) > 0:
        messages.append({"role": "user", "content": content})
        payload.append({"role": "user", "content": content})

    response = openai.ChatCompletion.create(
      model=model,
      messages=payload,
      temperature=temperature,
      top_p=top_p,
      frequency_penalty=frequency_penalty,
      presence_penalty=presence_penalty
      #max_tokens=max_length
    )
    
    usedTokens = response['usage']['total_tokens']

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
    
    return [format_message_data(), content, get_save_files(), historyLength, usedTokens ]

def update_array(array_number, update_content):
    messages[array_number]["content"] = update_content
    return format_message_data()


if is_api_key_set():
    set_api_key()   

css = "div.user {background-color:rgba(236,236,241,var(--tw-text-opacity)); text-align:right; }"
css += "div.assistant {background-color: rgba(68,70,84,var(--tw-bg-opacity)); color: rgba(236,236,241,var(--tw-text-opacity));}"
css += ".user,.assistant {padding: 15px 10px 15px 10px; margin:15px; border-radius: 5px;}"
css += "code {background-color: black; color: white; margin: 15px 10px 15px 10px; padding: 10px; display: inline-block;}"
css += ".chat_container {background-color:rgb(249 250 251 / var(--tw-bg-opacity)); padding: 5px; border-radius: 3px; min-height:100px; font-size:1.2rem;}"
css += ".dark .chat_container {background-color:rgb(17 24 39 / var(--tw-bg-opacity));}" 
css += ".dark .user {background-color:#66666d; color: rgb(229 231 235 / var(--tw-text-opacity));}"

with gr.Blocks(css=css, title="Simple Chat") as demo: 
    with gr.Row(visible=(not is_api_key_set())) as api_key_setup:
        with gr.Column(scale=1):
            api_key_box = gr.Textbox(label="Set the OpenAPI key (visit https://platform.openai.com/account/api-keys to generate a key)")
            submit_api_key = gr.Button("Submit", variant='primary')
            
    output = gr.HTML(value=format_message_data)
    
    with gr.Row(variant="panel").style(equal_height=False):
        with gr.Column(scale=1):
            editor = gr.Button("Editor", elem_id="editor")
            close_editor = gr.Button("Close Editor", visible=False)
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
    with gr.Row():
        update_content = gr.Textbox(label="Update message by clicking on the chat message to edit", lines=5, visible=False, elem_id="update_content")
        array_number = gr.Number(label="Array Number", visible=False, precision=0, elem_id="array_number")
    
    update = gr.Button("Update", visible=False)
    
    with gr.Row(variant="panel") as submit_row:
        with gr.Column(scale=30):
            submit = gr.Button("Submit", variant='primary')
        with gr.Column(scale=1):
            regenerate = gr.Button(value="Regenerate")
    
    with gr.Accordion(label="Settings:", open=False):
        with gr.Row():
            with gr.Column(visible=False):
                max_length = gr.Slider(minimum=1, maximum=4096, step=1, label="Max Length", value=4096, interactive=True)
            with gr.Column():
                temperature = gr.Slider(minimum=0, maximum=1, step=0.01, label="Temperature", value=1, interactive=True)
                top_p = gr.Slider(minimum=0, maximum=1, step=0.01, label="Top P", value=1, interactive=True)
            with gr.Column():
                frequency_penalty = gr.Slider(minimum=-2, maximum=2, step=0.01, label="Frequency Penalty", value=0, interactive=True)
                presence_penalty = gr.Slider(minimum=-2, maximum=2, step=0.01, label="Presence Penalty", value=0, interactive=True)
        with gr.Row():
            # controls the number of messages in history to include in the context. A hacky way to avoid exceeding the token limit for now.
            historyLength = gr.Slider(label='Message History Limit', minimum=1, maximum=100, step=1, value=30,)
            with gr.Column():
                with gr.Row():
                    prevGenLen = gr.Number(label='Previous Gen History Limit')
                    prevTokenTotal = gr.Number(label='Previous Gen Token Total (Max: 4096)')
        with gr.Row():
            with gr.Column():
                model = gr.Dropdown(get_models(), label="Model", value="gpt-3.5-turbo")

        
    #Bindings
    submit.click(fn=chat, inputs=[context, content, file_name, autosave, autoclear, max_length, temperature, top_p, frequency_penalty, presence_penalty, historyLength, model], outputs = [output, content, file_dropdown, prevGenLen, prevTokenTotal])
    regenerate.click(fn=regenerate_response, inputs=[context, content, file_name, autosave, autoclear, max_length, temperature, top_p, frequency_penalty, presence_penalty, historyLength, model], outputs = [output, content, file_dropdown, prevGenLen, prevTokenTotal])
    clear.click(fn=clear_chat,inputs=None, outputs = [output, file_name], show_progress=False)
    file_dropdown.change(fn=load_save_file, inputs=[file_dropdown, context, file_name], outputs=[output, context, file_name, file_dropdown])
    submit_api_key.click(fn=set_new_api_key, inputs=api_key_box, outputs=api_key_setup)
    
    #actions when clicking the editor button
    editor.click(fn=hide,outputs=content)
    editor.click(fn=hide,outputs=submit_row)
    editor.click(fn=hide,outputs=editor)
    editor.click(fn=show,outputs=close_editor)
    editor.click(fn=show,outputs=update)
    editor.click(fn=show,outputs=update_content)
    
    #actions when closing the editor
    close_editor.click(fn=show,outputs=content)
    close_editor.click(fn=show,outputs=submit_row)
    close_editor.click(fn=show,outputs=editor)
    close_editor.click(fn=hide,outputs=close_editor)
    close_editor.click(fn=hide,outputs=update)
    close_editor.click(fn=hide,outputs=update_content)
    
    update.click(fn=update_array,inputs=[array_number, update_content],outputs=output)
    
demo.launch(inbrowser=True)