from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import random
from model import GeneralModel
from time import sleep


"""
# LITTLE CHARADES
"""

class Application:
    _model = None
    _api_key = None
    _riddle_count = 0
    _enable_debug = False

    keys = []

    def __init__(self, riddle_count, gptModel):
        self._model = gptModel
        self._riddle_count = range(riddle_count)
        if "error" not in st.session_state:
            st.session_state.error = False
        if "expanded" not in st.session_state:
            st.session_state.expanded = True
        if "answer_state" not in st.session_state:
            st.session_state.answer_state = [None] * riddle_count
        if "wait" not in st.session_state:
            st.session_state.wait = False
        for wordidx in self._riddle_count:
            key_str = f"key{wordidx}val" 
            if key_str not in st.session_state:
                st.session_state[key_str] = ""

    def play_again(self):
        st.session_state.error = False
        st.session_state.expanded = True
        st.session_state.answer_state = [None] * len(self._riddle_count)
        for wordidx in self._riddle_count:
            key_str = f"key{wordidx}val" 
            st.session_state[key_str] = ""

    def check_answer(self, idx):
        if not st.session_state[f"answer{idx}val"]:
            return
        states = [st.session_state[f"answer{i}val"] == st.session_state[f"key{i}val"]
                    for i in self._riddle_count]

        if states[int(idx)] == True:
            st.session_state.answer_state[int(idx)] = True
        else:
            st.session_state.answer_state[int(idx)] = False

        if all(st.session_state.answer_state):
            st.balloons()

    def get_things(self):
        st.session_state.expanded = False
        categories = st.session_state[f"categories"]
        categories = categories.split(';')
        categories = [c.strip('; ') for c in categories]
        category = random.choice(categories)
        words, query = self._model.get_things(len(self._riddle_count), category, self._api_key)
        for idx, w in enumerate(words):
            st.session_state[f"key{idx}val" ] = w
        riddles, queryr, out_dbg = self._model.get_riddles(words, self._api_key)
        if riddles:
            st.session_state[f"riddleval" ] = riddles
        else:
            st.session_state[f"riddleval" ] = "SORRY ERROR OCCURED :( TRY AGAIN"
            st.session_state.error = True
            
        
        self.debug_set(f"debug_riddleall", out_dbg)
        self.debug_set(f"debug_wordsall", " ".join(words))
        self.debug_set(f"debug_query", query)
        self.debug_set(f"debug_queryriddle", queryr)

    def sidebar(self):
        self._api_key = st.sidebar.text_input("APIkey", type="password", value="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")
        txt = st.sidebar.text_area('CATEGORIES (seprate with ;)', '''kitchen; cars; living room; technology; cinema; home; bathroom; human; nature; forest''', key="categories")
        with st.sidebar.expander("ANSWERS! (check only if you MUST)", expanded=st.session_state.expanded):
            for wordidx in self._riddle_count:
                self.keys.append(st.text_input(f"Riddle answer {wordidx}:", key=f"key{wordidx}val"))
    
    def window(self):
        if not self._api_key:
            st.error("🔑 Please enter API Key")
            return

        if all(self.keys):
            if all(st.session_state.answer_state):
                st.header("BRAVO you won!")
                st.button("PLAY AGAIN", key=f"playagain", on_click=self.play_again)
            elif st.session_state.error:
                st.error("SORRY error occured :( Please try again!")
                st.button("PLAY AGAIN", key=f"playagain", on_click=self.play_again)
            else:
                st.header("Let the game begin :clapper:")
                st.subheader("Enter the names in order they are described:")
            st.text_area('', '', key=f"riddleval", disabled=True, label_visibility="collapsed")
            keyscols = st.columns(len(self.keys))
            for idx, col in enumerate(keyscols):
                with col:
                    if st.session_state.answer_state[idx] is None:
                        st.info("PROVIDE YOUR ANSWER")
                    elif st.session_state.answer_state[idx] == False:
                        st.error("TRY AGAIN!")
                    elif st.session_state.answer_state[idx] == True:
                        st.success("BRAVO!")
                    st.text_input("", key=f"answer{str(idx)}val", value="", label_visibility="collapsed")
                    st.button("CHECK!", key=f"check{str(idx)}", on_click=self.check_answer, args=(str(idx)))

        else:
            st.header("Can you guessa a name of object by the description ?")
            st.button("HIT THE BUTTON AND START THE GAME❕", on_click=self.get_things)
    def debug(self):
        st.text_area('', '', key=f"debug_query", disabled=True, label_visibility="collapsed")
        st.text_area('', '', key=f"debug_wordsall", disabled=True, label_visibility="collapsed")
        st.text_area('', '', key=f"debug_riddleall", disabled=True, label_visibility="collapsed")
        st.text_area('', '', key=f"debug_queryriddle", disabled=True, label_visibility="collapsed")

    def debug_set(self, key, value):
        if self._enable_debug:
            st.session_state[key] = value

    def render(self):
        self.sidebar()
        self.window()
        if self._enable_debug:
            self.debug()


numer_of_riddles = 3
model = GeneralModel()
app = Application(numer_of_riddles, model)
app.render()
