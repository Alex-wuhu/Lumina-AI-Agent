from app.utils.helper_functions import Visualize_Graph
from app.services.LLM_service import get_response
#Visualize_Graph()
query = "what is the topic of this document"

print(get_response(query))