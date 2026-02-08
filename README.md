# Data Analysis Agent

## How to Run the Application

Follow these step-by-step instructions to set up and run the Data Analysis Agent on your local machine using the Command Prompt (cmd) or PowerShell.

### Prerequisites

*   **Python 3.8+**: Ensure Python is installed. Verify with `python --version`.
*   **Git**: Ensure Git is installed. Verify with `git --version`.
*   **OpenAI API Key**: You need an API key from OpenAI (or a compatible provider).

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/rohanjangra07/data-analysis-agent.git
    cd data-analysis-agent
    ```

2.  **Set Up the Virtual Environment**
    It is recommended to use a virtual environment to manage dependencies.
    ```powershell
    # Create virtual environment
    python -m venv venv

    # Activate virtual environment (Windows)
    .\venv\Scripts\activate
    ```
    *Note: If you see an error about script execution policies, you can run the following command instead to use the python executable directly:*
    ```powershell
    # Alternative to activation
    .\venv\Scripts\python.exe -m pip ...
    ```

3.  **Install Dependencies**
    ```powershell
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root directory and add your API key:
    ```env
    OPENAI_API_KEY=your_api_key_here
    OPENAI_BASE_URL=https://openrouter.ai/api/v1  # Optional: if using OpenRouter
    ```

### Running the Application

1.  **Start the Streamlit Server**
    Run the following command in your terminal:
    ```powershell
    streamlit run app.py
    ```
    *   If you didn't activate the virtual environment, use:
        ```powershell
        .\venv\Scripts\python.exe -m streamlit run app.py
        ```

2.  **Access the Application**
    *   The application should automatically open in your default web browser.
    *   If not, navigate to `http://localhost:8501`.

### Usage Guide

1.  **Upload Data**: Click "Browse files" in the sidebar to upload a CSV file (e.g., `data/sample_sales.csv`).
2.  **Ask Questions**: Type your question in the chat input at the bottom.
    *   *Example: "What are the total sales for each product?"*
    *   *Example: "Show me the trend of sales over time."*
3.  **View Results**: The agent will process your request and provide a natural language answer. The technical details are handled in the background.

### Troubleshooting

*   **"Path not found" error**: Make sure you are in the correct directory (`cd "C:\Users\rohan\data analsyis agent"`).
*   **"streamlit is not recognized"**: Ensure you have activated the virtual environment or are using `python -m streamlit`.
*   **API Key Errors**: Check your `.env` file or enter the key manually in the sidebar.