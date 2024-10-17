import streamlit as st
import google.generativeai as genai
import google.ai.generativelanguage as glm
from dotenv import load_dotenv
from PIL import Image
import os
import io, time

load_dotenv()

def image_to_byte_array(image: Image) -> bytes:
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

st.header("Max AI")
st.write("")

gemini_pro, gemini_flash = st.tabs(["Gemini Pro", "Gemini-flash"])


def main():
    with gemini_pro:
        st.header("Hello Welcome What is question...?")
        st.write("")

        prompt = st.text_input(
            "Enter your question please...",
            placeholder="Question",
            label_visibility="visible",
        )
        model = genai.GenerativeModel("gemini-pro")

        if st.button("SUMBIT", use_container_width=True):
            response = model.generate_content(prompt)

            st.write("")
            st.header(":red[Response]")
            st.write("")

            st.markdown(response.text)

    with gemini_flash:
        st.header("Interact with Gemini Pro Vision")
        st.write("")

        image_prompt = st.text_input(
            "Interact with the Image/Video",
            placeholder="Prompt",
            label_visibility="visible",
        )
        uploaded_file = st.file_uploader(
            "Choose and Image",
            accept_multiple_files=False,
            type=["png", "jpg", "jpeg", "webp", "mp4", "mkv"],
        )

        if uploaded_file is not None:
            model = genai.GenerativeModel("gemini-1.5-flash")
            if uploaded_file.name.endswith((".mp4", ".mkv")):
                st.video(uploaded_file, autoplay=True)
                if st.button("GET RESPONSE", use_container_width=True):

                    with open(uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    myfile = genai.upload_file(uploaded_file.name)
                    while myfile.state.name == "PROCESSING":
                        time.sleep(0.5)
                        myfile = genai.get_file(myfile.name)

                    result = model.generate_content(
                        [myfile, image_prompt or "Describe this video clip"]
                    )
                    result.resolve()

                    st.write("")
                    st.write(":green[Response]")
                    st.write("")

                    st.markdown(result.text)

            else:
                st.image(Image.open(uploaded_file), use_column_width=True)

                st.markdown(
                    """
                <style>
                        img {
                            border-radius: 50px;
                        }
                </style>
                """,
                    unsafe_allow_html=True,
                )

                if st.button("GET RESPONSE", use_container_width=True):
                    if uploaded_file is not None:
                        if image_prompt != "":
                            image = Image.open(uploaded_file)

                            response = model.generate_content(
                                glm.Content(
                                    parts=[
                                        glm.Part(text=image_prompt),
                                        glm.Part(
                                            inline_data=glm.Blob(
                                                mime_type="image/jpeg",
                                                data=image_to_byte_array(image),
                                            )
                                        ),
                                    ]
                                )
                            )

                            response.resolve()

                            st.write("")
                            st.write(":red[Response]")
                            st.write("")

                            st.markdown(response.text)

                    else:
                        st.write("")
                        st.header(":red[Please Provide a prompt]")

                else:
                    st.write("")
                    st.header(":red[Please Provide an image]")

main()
