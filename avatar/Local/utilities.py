
def language_selection(lang:str): 
        if lang == 'en':        
                        # Language in which you want to convert
            language = 'en'
            langlang='English'
        elif lang == 'es':        
            # Language in which you want to convert
            language = 'es'
            langlang='Spanish'
        elif lang=='de':
            language='de'
            langlang='German'
        else:
            print("Please enter a valid language")
        return language, langlang
    
def text_chat(input_text,st,promp_template,demo):
    if input_text: 
    
        with st.chat_message("user"): 
            st.markdown(input_text) 
        
        st.session_state.chat_history.append({"role":"user", "text":promp_template}) 

        chat_response = demo.demo_conversation(input_text=input_text, memory=st.session_state.memory) #** replace with ConversationChain Method name - call the model through the supporting library
        
        with st.chat_message("assistant"): 
            st.markdown(chat_response) 

        
        st.session_state.chat_history.append({"role":"assistant", "text":promp_template}) 
    
