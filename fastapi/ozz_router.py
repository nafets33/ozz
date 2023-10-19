


@router.post("/voiceGPT", status_code=status.HTTP_200_OK)
def load_ozz_voice(api_key=Body(...), text=Body(...), self_image=Body(...)):
    # print(kwargs)
    # text = [{'user': 'hey hootie tell me a story'}]
    # text = [  # future state
    #         {'user': 'hey hootie tell me a story', 'resp': 'what story would you like to hear'}, 
    #         {'user': 'could you make up a story?'}]
    ipdb.set_trace()
    def handle_response(text):
        text_obj = text[-1]['user']

        # handle text_obj
        # WORK take query/history of current question and attempt to handle reponse back ""
        ## Scenarios 

        call_llm=True # goal is to set it to False and figure action/response

        def Scenarios(db_actions, self_image, current_query, first_ask=True, conv_history=False):
            # is this first ask?
            # saying hello, say hello based on whos talking? hoots or hootie, moody
            # how are you...
            # 
            # if first_ask:
            #     # based on question do we have similar listed type quetsion with response action?
            #     if current_query is in db_actions.get('db_first_asks'):
            #         text = db_actions.get('id')
            #         self_image = db_actions.get('id')
                
            return True

        # get final response
        resp = 'what story would you like to hear?'
        
        # update reponse to self
        text[-1].update({'resp': resp})

        return text

    text = handle_response(text)
    
    def handle_image(text, self_image):
        # based on LLM response handle image if needs to change
        self_image = '/Users/stefanstapinski/ENV/pollen/pollen/custom_voiceGPT/frontend/build/hootsAndHootie.png'

        return self_image

    self_image = handle_image(text, self_image)
    
    # audio_file = 'pollen/db/audio_files/file1.mp4'
    audio_file = '/Users/stefanstapinski/ENV/pollen/pollen/custom_voiceGPT/frontend/build/test_audio.mp3'
    
    json_data = {'text': text, 'audio_path': audio_file, 'page_direct': None, 'self_image': self_image}


    return JSONResponse(content=json_data)