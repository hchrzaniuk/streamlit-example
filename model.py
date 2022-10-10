import openai

get_riddles_prompt = """Describe {count} objects as it would be 10 year old child do but do not use name of it in description. {things}"""
get_riddles_prompt_1 = """Describe {count} objects but do not use name of it in description. {things}"""
get_things_prompt = """Get names of {count} random objects related to {category}."""

def set_openai_key(key):
    """Sets OpenAI key."""
    openai.api_key = key

class GeneralModel:
    def __init__(self):
        print("Model Intilization--->")
        # set_openai_key(API_KEY)

    def query(self, prompt, myKwargs={}):
        """
        wrapper for the API to save the prompt and the result
        """

        # arguments to send the API
        kwargs = {
            "engine": "text-davinci-002",
            "temperature": 1,
            "max_tokens": 600,
            "best_of": 1,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": ["###"],
        }


        for kwarg in myKwargs:
            kwargs[kwarg] = myKwargs[kwarg]


        ret = openai.Completion.create(
                prompt=prompt, **kwargs)["choices"][0]["text"].strip()
        return ret

    def get_riddles(self, inputs, api_key):
        set_openai_key(api_key)
        output_debug = ""
        retry = 3
        inputs = [x.lower().strip(',.<> ') for x in inputs]
        inputs_joined = "\n"
        inputs_joined += "\n".join(inputs)
        prompt = get_riddles_prompt_1.format(count = len(inputs), things = inputs_joined)
        while retry:
            retry -= 1
            output = self.query(prompt)
            output_debug += f"\n{retry}\n{output}"
            check = [i in output for i in inputs]
            if any(check):
                # riddle contains answer
                continue
            if not output:
                # output empty
                continue
            return output, prompt, output_debug
        return None, prompt, output_debug

    def get_things(self, count, category, api_key):
        set_openai_key(api_key)
        output = ""
        retry = 2
        prompt = get_things_prompt.format(count = str(count), category = category)
        in_progress = True
        while retry:
            retry -= 1
            output = self.query(prompt)
            if '?' in output:
                # sometimes GPT asks questions
                continue
            if len(output.split(",")) != count:
                continue
            output = output.split(",")
            output = [w.lower().strip(',.<> ') for w in output]
            return output, prompt
        return [None] * count, prompt