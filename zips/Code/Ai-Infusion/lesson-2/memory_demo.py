from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from summarizer_langchain import model

prompt = ChatPromptTemplate.from_messages([
            ("system", "you are friendly tutor"),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ])

chain = prompt | model

history = [HumanMessage("My Name is Raghuram"), AIMessage("Hi Raghuram!")]

if __name__ == "__main__":
    print(chain.invoke({"history": history, "question" : "what is my name?"}).content)