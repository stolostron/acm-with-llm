import os
import argilla as rg
from dotenv import load_dotenv, find_dotenv

# You need to use Argilla admin creds
# else you will get a 403 error
# when trying to push the dataset into Argilla
# I guess this is because we are pushing 
# into an existing workspace called admin
# Note we create the data set only once
def callback():
    print("Initializing Argilla Callback!")

    dataset = rg.FeedbackDataset(
    fields=[
        rg.TextField(name="prompt"),
        rg.TextField(name="response"),
    ],
    questions=[
        rg.RatingQuestion(
            name="response-rating",
            description="How would you rate the quality of the response?",
            values=[1, 2, 3, 4, 5],
            required=True,
        ),
        rg.TextQuestion(
            name="response-feedback",
            description="What feedback do you have for the response?",
            required=False,
        ),
    ],
    guidelines="You're asked to rate the quality of the response and provide feedback.",
    )
    _ = load_dotenv(find_dotenv()) 

    rg.init(
        #api_url=os.environ["ARGILLA_API_URL"],
        #api_key=os.environ["ARGILLA_API_KEY"],
        workspace="admin",
        api_url=os.getenv('ARGILLA_API_URL'),
        api_key=os.getenv('ARGILLA_API_KEY'),
    )
    dataset_list = rg.FeedbackDataset.list(workspace="admin")

    langchain_dataset_exist = False

    for datasetexist in dataset_list:
        print(datasetexist.name)
        if datasetexist.name == "langchain-dataset":
            langchain_dataset_exist = True
        print("langchain-dataset exists!!!")

    if langchain_dataset_exist == False:    
        dataset.push_to_argilla(name="langchain-dataset",workspace="admin")
    
    return rg.FeedbackDataset.from_argilla(name='langchain-dataset',workspace='admin')

def add_record(prompt, response,dataset):
    # Create a record object
    record = rg.FeedbackRecord(
        fields={
            "prompt": prompt,
            "response": response
        })
    dataset.add_records(record)
    return record
                 