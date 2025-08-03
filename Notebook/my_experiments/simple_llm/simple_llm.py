import getpass
import os

try:
	from dotenv import load_dotenv
	load_dotenv()

except ImportError:
	pass

os.environ["LANGSMITH_TRACING"] = "true"
if "LANGSMITH_API_KEY" not in os.environ:
	os.environ["LANGSMITH_API_KEY"] = getpass.getpass(
		prompt = "Enter Your LangSmith API Key (optional)")

if "LANGSMITH_PROJECT" not in os.environ:
	os.environ["LANGSMITH_PROJECT"] = getpass.getpass(
		prompt = "Enter you LangSmith Project Name (default = 'default')")

	if not os.environ.get("LANGSMITH_PROJECT"):
		os.environ["LANGSMITH_PROJECT"] = "default"

if not os.environ.get("GOOGLE_API_KEY"):
	os.environ["GOOGLE_API_KEY"] = getpass.getpass(
		"API key for  Google Gemini")

from langchain.chat_models import init_chat_model

model = init_chat_model("gemini-2.5-flash", model_provider = "google_genai")

from langchain_core.messages import HumanMessage, SystemMessage

messages = [
	SystemMessage("Translate the Following from English into Tamil"),
	HumanMessage("HI!")
]

model.invoke(messages)

# the following are equivalent

model.invoke("hello")

model.invoke([{'role': 'user', 'content': 'hello'}])

model.invoke([HumanMessage("hello")])

# Streaming
for token in model.stream(messages):
	print(token.content, end = "|")


# Prompt Templates

from langchain_core.prompts import ChatPromptTemplate

system_template = "Translate the following from English into {language}"

prompt_template = ChatPromptTemplate.from_messages(
	[("system", system_template),
	 ("user", "{text}")])


prompt = prompt_template.invoke({"language": "Italian", "text": "hi!"})

# the following print the complete prompt after filling placeholders
prompt.to_messages()

response = model.invoke(prompt)
print(response.content)
