from django.db import models
import json, os
import openai

from openai import OpenAI
# api key goes here 
client = OpenAI(api_key = "API KEY GOES HERE")

class Replacer(models.Model):

    def __init__(self):
        script_dir = os.path.dirname(__file__)  # Absolute dir the script is in
        rel_path = "sample.json"
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, "r") as json_file:
            self.sentences = json.load(json_file)
    def clean_json_string(self, json_str):
        # Remove backslashes and newline characters
        cleaned_str = json_str.replace("\\", "").replace("\n", " ")
        return cleaned_str
    def generate_simplifications(self, text):
        try:

            # Grade-aware prompt suffix using gradePromptSuffix
            gradePromptSuffix = ""
            
            if grade == "Elementary":
                gradePromptSuffix = "For all simplifications, use short, easy to read sentences and words an elementary student would know."
            elif grade == "High School":
                gradePromptSuffix = "For all simplifications, use clear, conversational language familiar to a high school reader."
            elif grade == "College":
                gradePromptSuffix = "For all simplifications, maintain semantic integrity and allow some domain-specific vocabulary suitable for a college-level reader."
        

            instruction = f"""
            For the given sentence: "{text}", perform the following tasks:

            1. Identify all complex or uncommon words and list simpler synonyms. Focus on words that a general reader or non-native speaker might find difficult, and ensure the suggested synonyms preserve the original meaning.
            2. Rewrite using simpler vocabulary. Replace complex or rare terms with more common synonyms while keeping the meaning unchanged. Simplify as many words as possible, ensuring the sentence remains grammatically correct and semantically accurate.
            3. Paraphrase in simpler, more straightforward language. Use clear, everyday wording without omitting important details. The meaning should remain exactly the same, expressed in accessible terms.
            4. Rewrite with simpler syntax. Break down long or complex sentence structures into shorter, clearer ones while preserving the original meaning.
            5. Simplify both vocabulary and sentence structure. Replace difficult words with easier synonyms and split up complex constructions if needed. Ensure the result is fluent, easy to read, and faithful to the original meaning.
            Format the response as follows:
            
            "{text}": {{ 
                "lexical": "Simplified sentence with lexical changes.",
                "words": {{
                    "complex_word1": "simple_word1", 
                    "complex_word2": "simple_word2",
                    ...
                }}, 
                "syntactic": "Simplified sentence with syntactic changes.",
                "syntactic_and_lexical": "Sentence with both syntactic and lexical changes."
            }}
            """
            
            # Combine the gradePromptSuffix and instruction to form the full prompt
            promptText = gradePromptSuffix + instruction
            
            # Debugging: Print parts of the prompt separately to check each part
            print("Grade level prompt suffix:", gradePromptSuffix)  # Log the grade level suffix
            print("Instruction text:", instruction)  # Log the instruction text
            print("Generated Prompt with grade level:", promptText)  # Log the full prompt
            
            # The rest of your API call or further processing would go here
            return promptText

            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Simplify complex sentences by identifying complex words and simplifying sentence structure."},
                    {"role": "user", "content": instruction}
                ]
            )
            simplified_text = response.choices[0].message.content
            # print("Simplified Text ", simplified_text)
            # .choices[0].message.content
            return self.clean_json_string(simplified_text)
        except Exception as e:
            print(f"Error while calling OpenAI API: {e}")
            return None

    def replaceSentence(self, to_replace):
        print("Sentence to be replaced ----->", to_replace)
        try:
            if to_replace in self.sentences:
                return self.sentences[to_replace]

            sentence = self.generate_simplifications(to_replace)
            if sentence:
                try:
                    # Extract only the JSON part of the response
                    # Split at the first colon, and take the part after it
                    json_part = sentence.split(":", 1)[1].strip()
                    res = json.loads(json_part)
                    self.sentences[to_replace] = res
                    self.save_to_json()
                    return res
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON: {e}")
                    return {}
        except Exception as ex:
            print(f"Error in replaceSentence: {ex}")
            return {}
    # def clean_json_string(json_str):
    #     # Remove backslashes and newline characters
    #     cleaned_str = json_str.replace("\\", "").replace("\n", "")
    
    #     return cleaned_str


    def save_to_json(self):
        script_dir = os.path.dirname(__file__)  # Absolute dir the script is in
        rel_path = "sample.json"
        abs_file_path = os.path.join(script_dir, rel_path)
        # print("Save to JSON PRINT", self.sentences)
        # self.sentence = self.clean_json_string(self.sentence)
        try:
            with open(abs_file_path, "w") as json_file:
                json.dump(self.sentences, json_file, indent=4)
            print("Successfully saved simplifications to sample.json")
        except Exception as e:
            print(f"Failed to save to sample.json: {e}")
