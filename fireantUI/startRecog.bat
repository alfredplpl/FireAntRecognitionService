cd C:\Users\misok\PycharmProjects\fireantRecognition
forever start -a -l C:\Users\misok\NodeJSProject\fireantUI\logs\foreverRecog.log -o C:\Users\misok\NodeJSProject\fireantUI\logs\outRecog.log -e C:\Users\misok\NodeJSProject\fireantUI\logs\errRecog.log -c python .\predictImage.py
cd C:\Users\misok\NodeJSProject\fireantUI
