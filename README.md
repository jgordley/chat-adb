# ADB Chat

ADB Chat is a [LangChain](https://github.com/langchain-ai/langchain) Agent-based chat application that allows the user to execute [Android Debug Bridge](https://developer.android.com/tools/adb) commands using a natural language chat interface.

![ADB Chat Homepage](/screenshots/homepage.png)

Research Paper: [ADB Chat: A Chat-based Langchain Agent for
Android Forensics](https://www.dropbox.com/scl/fi/kka39ii05idqw76gnqajz/ADB_Chat_Final_Report.pdf?rlkey=tk6d2404uyha84n5e86jwtd3k&dl=0)

## Installation

1. Clone this repository locally and install the requirements using pip

```
➜ pip install -r requirements.txt
```

2. Install the Android Debug Bridge here: [Android Debug Bridge Download](https://developer.android.com/tools/adb)
    * At the bare minimum you need `/platform_tools` on your computer, here is the direct download page: [Platform Tools](https://developer.android.com/tools/releases/platform-tools)

## Usage

1. Start up an `adb` server on your computer
```
➜ adb start-server

daemon not running; starting now at tcp:5037
daemon started successfully
```

2. Start up the ADB Chat application
```
➜ streamlit run main.py

You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.196:8501

```

3. Enter your OpenAI API Key and output folder in the sidebar. Select a device and an OpenAI model to use.


## Troubleshooting
* If your sidebar dropdown is empty and does not show any device serial numbers, try to follow the troubleshooting steps shown here: [https://developer.android.com/tools/adb#Enabling](https://developer.android.com/tools/adb#Enabling)
* You can also try restarting the `adb` server like so:
```
➜ adb kill-server
➜ adb start-server
```
* Make sure you are entering your OpenAI API Key correctly if you are seeing 400 forbidden errors


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)