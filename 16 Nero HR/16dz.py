import json
import os
import pickle
import re
import textwrap

import tiktoken
from google.colab import drive, output, userdata
from IPython.display import clear_output
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
