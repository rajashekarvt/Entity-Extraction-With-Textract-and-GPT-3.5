import os

import boto3
import openai
import pandas as pd
import pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from trp import Document

from prompts import example_input_1, example_output_1, system_role

load_dotenv()

AWS_REGION = os.environ["AWS_REGION"]
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENVIRONMENT = os.environ["PINECONE_ENVIRONMENT"]
PINECONE_INDEX = os.environ["PINECONE_INDEX"]


client = boto3.client(
    "textract",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

index = pinecone.Index(PINECONE_INDEX)


def get_response(image):
    response = client.detect_document_text(Document={"Bytes": image})
    text = ""
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            print(item["Text"])
            text += f" {item['Text']}"

    return text


model_name = "all-minilm-l6-v2"
model = SentenceTransformer(model_name)


def get_matching_doc_type(ocr_text):
    query = ocr_text
    xq = model.encode([query]).tolist()
    result = index.query(xq, top_k=1, include_metadata=True)
    return result["matches"][0]["metadata"]["doctype"]


def extract_entities(text):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": example_input_1},
            {"role": "assistant", "content": example_output_1},
            {"role": "user", "content": f"OCR Text:\n{text}"},
        ],
        stream=True,
        temperature=0,
    )
    # return response["choices"][0]["message"]["content"]
    return response


def extract_entities_with_textract(*args, **kwargs):
    s3 = boto3.resource(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )

    s3BucketName = "sample-bucket-doc"
    s3.create_bucket(Bucket=s3BucketName)
    documentName = "image.jpg"
    s3.Bucket(s3BucketName).upload_file(documentName, documentName)
    response = client.analyze_document(
        Document={"S3Object": {"Bucket": s3BucketName, "Name": documentName}},
        FeatureTypes=["FORMS", "TABLES"],
    )

    doc = Document(response)
    text = "Entities:\n"
    for page in doc.pages:
        for field in page.form.fields:
            text += f"{field.key}: {field.value}\n"

    return text, response


def extract_tables(response):
    dataframes = []
    blocks = response["Blocks"]
    tables = map_blocks(blocks, "TABLE")
    cells = map_blocks(blocks, "CELL")
    words = map_blocks(blocks, "WORD")
    selections = map_blocks(blocks, "SELECTION_ELEMENT")
    for table in tables.values():
        table_cells = [cells[cell_id] for cell_id in get_children_ids(table)]
        n_rows = max(cell["RowIndex"] for cell in table_cells)
        n_cols = max(cell["ColumnIndex"] for cell in table_cells)
        content = [[None for _ in range(n_cols)] for _ in range(n_rows)]
        for cell in table_cells:
            cell_contents = [
                words[child_id]["Text"]
                if child_id in words
                else selections[child_id]["SelectionStatus"]
                for child_id in get_children_ids(cell)
            ]
            i = cell["RowIndex"] - 1
            j = cell["ColumnIndex"] - 1
            content[i][j] = " ".join(cell_contents)
        dataframe = pd.DataFrame(content[1:], columns=content[0])
        dataframes.append(dataframe)
    return dataframes


def map_blocks(blocks, block_type):
    return {block["Id"]: block for block in blocks if block["BlockType"] == block_type}


def get_children_ids(block):
    for rels in block.get("Relationships", []):
        if rels["Type"] == "CHILD":
            yield from rels["Ids"]
