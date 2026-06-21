
from flask import Flask, render_template, request
from google import genai
from dotenv import load_dotenv
import os
from PIL import Image

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
load_dotenv()

apikey = os.getenv("API-KEY")
client = genai.Client(
    api_key=apikey
)
foldersup = "uploads"
app.config["foldersup"] = foldersup

if not os.path.exists(foldersup):
    os.makedirs(foldersup)


@app.route("/", methods=["GET", "POST"])
def index():

    result = None
    error = None

    if request.method == "POST":

        medicine_name = request.form.get("medicine_name", "").strip()
        uploaded_files = request.files.getlist("images")

        try:


            if medicine_name:

                prompt = f"""
                Provide detailed information about {medicine_name}.

                Include:

                1. Medication Name
                2. Purpose
                3. Active Ingredients
                4. Typical Dosage
                5. Possible Side Effects
                6. Warnings
                7. Drug Interactions

                Prediction Section:
                - Common side effect risk
                - Interaction risk
                - Adherence risk

                Format clearly with headings.
                """

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                result = response.text


            else:

                valid_images = []

                for file in uploaded_files:

                    if file and file.filename:

                        filepath = os.path.join(
                            app.config["foldersup"],
                            file.filename
                        )

                        file.save(filepath)

                        img = Image.open(filepath)

                        valid_images.append(img)

                if len(valid_images) < 1:
                    error = "Please upload at least 1 image or enter a medication name."

                elif len(valid_images) > 3:
                    error = "Maximum of 3 images allowed."

                else:

                    prompt = """
                    Analyze these medication images.

                    Identify:

                    1. Medication Name
                    2. Purpose
                    3. Ingredients
                    4. Dosage Instructions
                    5. Possible Side Effects
                    6. Warnings
                    7. Drug Interactions
                    8. Expiration Information if visible

                    Prediction Section:
                    - Common side effect risk
                    - Interaction risk
                    - Adherence risk

                    Format clearly with headings.
                    """

                    contents = [prompt]

                    for img in valid_images:
                        contents.append(img)

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents
                    )

                    result = response.text



        except Exception as e:

            error = str(e)

            print("\nGEMINI ERROR:")
            print(e)

    return render_template(
        "index.html",
        result=result,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
