import pandas as pd
import openai
import json
import io
import sys

class DataAnalystAgent:
    def __init__(self, df: pd.DataFrame, api_key: str, base_url: str = None):
        self.df = df
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.history = [
            {"role": "system", "content": self._create_system_prompt()}
        ]

    def _create_system_prompt(self):
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        df_info = buffer.getvalue()
        
        prompt = f"""You are an intelligent Data Analysis Agent. You are interacting with a user who is asking questions about a dataset.
        
        Here is the information about the dataset:
        {df_info}
        
        First 5 rows:
        {self.df.head().to_markdown()}
        
        Your Goal: Analyze the dataset to answer user questions using Python (pandas).
        
        Process:
        1. Understand the user's question.
        2. If you need to perform analysis, write Python code.
        3. The code will be executed in a restricted environment where the dataframe is available as `df`.
        4. You must helpful, conversational, and data-driven.
        
        Output Format:
        You can output text explanation directly.
        If you need to calculate something, output a JSON object with this key:
        {{"code": "import pandas as pd\\nresult = df..."}}
        
        The variable `df` is already loaded.
        Store the final result of your calculation in a variable named `result` so it can be captured.
        Do not generate charts unless asked (if asked, use matplotlib/seaborn and save to a generic path or just describe it, but for now we focus on text/numbers).
        
        Make sure to always reason about the data.
        """
        return prompt

    def process_message(self, user_message: str):
        self.history.append({"role": "user", "content": user_message})
        return self._handle_llm_response_v2(user_message)

    def _handle_llm_response_v2(self, user_message):
        # We will use tools/function calling style prompt manually for maximum control
        tools_prompt = """
        You have a tool called `execute_python`.
        If you need to calculate something, respond with a JSON object:
        {
            "thought": "Reasoning about what to do...",
            "action": "execute_python",
            "code": "import pandas as pd\\nresult = df['col'].mean()"
        }
        
        If you have the answer or don't need code, respond with JSON:
        {
            "thought": "Reasoning...",
            "action": "reply",
            "response": "The answer is..."
        }
        """
        
        messages = [self.history[0]] + [{"role": "system", "content": tools_prompt}] + self.history[1:]
        
        try:
            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                response_format={"type": "json_object"}
            )
            content = completion.choices[0].message.content
            print(f"DEBUG: Raw content from LLM: {content}") # Debug print
            
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if JSON is invalid
                return f"Error: The AI returned invalid JSON. Raw response: {content}", None
            
            # Handle potential list response
            if isinstance(data, list):
                if len(data) > 0:
                    data = data[0]
                else:
                    return "Error: Empty response from AI.", None
            
            if data.get("action") == "execute_python":
                code = data.get("code")
                if not code:
                     return "Error: No code provided in execute_python action.", None
                     
                # Execute code
                local_vars = {"df": self.df, "pd": pd}
                try:
                    # Capture stdout to redirect print statements
                    old_stdout = sys.stdout
                    redirected_output = sys.stdout = io.StringIO()
                    
                    exec(code, {}, local_vars)
                    
                    sys.stdout = old_stdout
                    stdout_output = redirected_output.getvalue()
                    
                    result = local_vars.get("result", None)
                    if result is None and stdout_output:
                        result = stdout_output.strip()
                    elif result is None:
                        result = "No result variable set and no output captured."
                    
                    # Feed result back to LLM
                    self.history.append({"role": "assistant", "content": json.dumps(data)})
                    self.history.append({"role": "system", "content": f"Execution Result: {result}"})
                    
                    # Get final conversational response
                    # For final response, we don't force JSON, we just want text
                    # We inject a specific instruction to ensure no code is shown
                    final_messages = self.history + [{"role": "system", "content": "IMPORTANT: Provide a natural language answer based on the execution result. Do NOT show the python code or technical details in your response. Just the answer."}]
                    
                    final_completion = self.client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=final_messages
                    )
                    final_response = final_completion.choices[0].message.content
                    self.history.append({"role": "assistant", "content": final_response})
                    return final_response, result # Return result for display if needed
                    
                except Exception as e:
                    return f"Error executing code: {e}", None
            else:
                response = data.get("response")
                if not response:
                     response = str(data) # Fallback
                self.history.append({"role": "assistant", "content": response})
                return response, None

        except Exception as e:
            return f"Error in processing: {e}", None
