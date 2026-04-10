import google.generativeai as genai

genai.configure(api_key="AIzaSyDgg4_klhZu7uDWaRFZh60-Rb4VIpSAnUE")

for model in genai.list_models():
    print(model.name)