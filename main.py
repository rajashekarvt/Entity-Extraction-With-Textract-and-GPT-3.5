import streamlit as st
from PIL import Image

from utils import (
    extract_entities,
    extract_entities_with_textract,
    extract_tables,
    get_matching_doc_type,
    get_response,
)

st.title("Document Processing with Advanced NLP Techniques")

st.sidebar.subheader("PROJECT DETAILS:")
st.sidebar.write("**With this Project, We Aim to do the Following:**")
st.sidebar.write("- Perform OCR on a given Image of a Document using Amazon Textract")
st.sidebar.write("- Identify the Type of Document Using Semantic Search")
st.sidebar.write("- Extract Entities Using a GPT Model and Textract")
st.sidebar.write("- Extract Tables for Selective Document Types")

document = st.file_uploader(
    "Upload a Document", type=["jpg", "png"], accept_multiple_files=False
)

if document:
    st.image(document)

button = st.button("Submit")


if document and button:
    st.subheader("OCR Text:")
    with st.spinner("Extracting Text..."):
        image_path = "image.jpg"
        image = Image.open(document)
        image.save(image_path, "JPEG")
        with open(image_path, "rb") as image:
            processed_image = bytearray(image.read())
        ocr_response = get_response(processed_image)
        st.info("Extracted Text Using Amazon Textract")
        with st.expander("See OCR Text"):
            st.write(ocr_response)

    with st.spinner("Identifying Doc Category Using Semantic Search.."):
        doctype = get_matching_doc_type(ocr_response)
        st.info("Identified Document Category using Semantic Search")
        st.subheader("Category For Document:")
        st.write(str(doctype).upper())

    with st.spinner("Extracting Entities From The Document Using GPT Model.."):
        st.subheader("Entities For Document:")
        res_box = st.empty()
        entity_chunks = []
        entities = extract_entities(ocr_response)
        for chunk in entities:
            if "content" in chunk["choices"][0]["delta"]:
                res = chunk["choices"][0]["delta"]["content"]
                entity_chunks.append(res)
                accumulated_entities = "".join(entity_chunks)
                res_box.code(f"{accumulated_entities}", language="json")

        st.info("Extracted Entities Using GPT-3.5-turbo Model (ChatGPT API)")

    with st.spinner("Extracting Entities From The Document Using Textract"):
        text, response = extract_entities_with_textract()
        st.code(text, language="json")
        st.info("Extracted Entities Using Amazon Textract")

    if str(doctype).upper().strip() in ["FORM", "INVOICE"]:
        with st.spinner("Extracting Tables From The Document..."):
            st.subheader("Tables:")
            dfs = extract_tables(response)
            for dataframe in dfs:
                st.dataframe(dataframe)
            if not dfs:
                st.info("No  Relevant Tables were Found in Document")
            else:
                st.info("Tables Extracted From Document Using Amazon Textract")

    st.success("Document has been Processed Sucessfully")
