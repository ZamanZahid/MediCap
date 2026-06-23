from flask import Flask, render_template, request
from google import genai
from dotenv import load_dotenv
import os
import re
from PIL import Image

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
load_dotenv()


def parse_medication_response(text):
    if not text:
        return None

    sections = {
        "Medication Name": "",
        "Purpose": "",
        "Active Ingredients": [],
        "Typical Dosage": "",
        "Side Effects": [],
        "Warnings": [],
        "Drug Interactions": [],
        "Prediction Analysis": {
            "Side Effect Risk": "",
            "Interaction Risk": "",
            "Adherence Risk": ""
        }
    }

    current = None
    lines = [line.strip() for line in text.replace("\r", "").splitlines()]

    for raw in lines:
        if not raw:
            continue

        line = re.sub(r'^(#{1,6}\s*)', '', raw).strip()

        heading = re.match(
            r'^(Medication Name|Purpose|Active Ingredients|Typical Dosage|Dosage Instructions|Possible Side Effects|Side Effects|Warnings|Drug Interactions|Prediction Section|Prediction Analysis)\s*[:\-–—]?\s*$',
            line,
            re.IGNORECASE,
        )

        if heading:
            key = heading.group(1).lower()
            if key in ["possible side effects", "side effects"]:
                current = "Side Effects"
            elif key == "dosage instructions":
                current = "Typical Dosage"
            elif key in ["prediction section", "prediction analysis"]:
                current = "Prediction Analysis"
            elif key == "active ingredients":
                current = "Active Ingredients"
            else:
                current = heading.group(1).title()
            continue

        risk_match = re.search(
            r'(Side Effect Risk|Interaction Risk|Adherence Risk)\s*[:\-–—]\s*(Low|Moderate|High)',
            line,
            re.IGNORECASE,
        )
        if risk_match:
            risk_name = risk_match.group(1).title()
            risk_value = risk_match.group(2).title()
            sections["Prediction Analysis"][risk_name] = risk_value
            continue

        if current == "Prediction Analysis":
            risk_match = re.search(
                r'^(Side Effect Risk|Interaction Risk|Adherence Risk)\s*[:\-–—]\s*(.+)$',
                line,
                re.IGNORECASE,
            )
            if risk_match:
                risk_name = risk_match.group(1).title()
                sections["Prediction Analysis"][risk_name] = risk_match.group(2).strip().title()
                continue

        list_match = re.match(r'^[\*\-•]\s*(.+)$', line)
        if list_match:
            item = list_match.group(1).strip()
            if current in ["Side Effects", "Warnings", "Drug Interactions", "Active Ingredients"]:
                sections[current].append(item)
            elif current:
                sections[current] += (" " if sections[current] else "") + item
            continue

        if current in ["Side Effects", "Warnings", "Drug Interactions", "Active Ingredients"]:
            if "," in line and len(sections[current]) <= 1:
                items = [item.strip() for item in line.split(",") if item.strip()]
                sections[current].extend(items)
            else:
                sections[current].append(line)
        elif current == "Prediction Analysis":
            risk_match = re.match(
                r'^(Side Effect Risk|Interaction Risk|Adherence Risk)\s*[:\-–—]\s*(.+)$',
                line,
                re.IGNORECASE,
            )
            if risk_match:
                risk_name = risk_match.group(1).title()
                sections["Prediction Analysis"][risk_name] = risk_match.group(2).strip()
        elif current:
            sections[current] += (" " if sections[current] else "") + line

    for key in ["Active Ingredients", "Side Effects", "Warnings", "Drug Interactions"]:
        values = []
        for item in sections[key]:
            if "," in item and len(sections[key]) == 1:
                values.extend([subitem.strip() for subitem in item.split(",") if subitem.strip()])
            else:
                values.append(item)
        sections[key] = values

    has_content = any(
        [
            sections["Medication Name"],
            sections["Purpose"],
            sections["Typical Dosage"],
            sections["Active Ingredients"],
            sections["Side Effects"],
            sections["Warnings"],
            sections["Drug Interactions"],
            any(sections["Prediction Analysis"].values()),
        ]
    )

    return sections if has_content else None


@app.route("/", methods=["GET", "POST"])
def index():

    result = None
    structured_result = None
    error = None

    if request.method == "POST":

        # Get API key from form data, request header, or environment
        api_key = request.form.get("api_key") or request.headers.get("X-API-Key") or os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            error = "API key not provided. Please enter your Gemini API key."
            return render_template(
                "index.html",
                result=result,
                structured_result=structured_result,
                error=error
            )
        
        client = genai.Client(api_key=api_key)

        medicine_name = request.form.get("medicine_name", "").strip()
        uploaded_files = request.files.getlist("images")

        try:


            if medicine_name:

                prompt = f"""
                Provide detailed information about {medicine_name}.

                Include:
                - Medication Name
                - Purpose
                - Active Ingredients
                - Typical Dosage
                - Possible Side Effects
                - Warnings
                - Drug Interactions

                Prediction Analysis:
                Side Effect Risk: Low, Moderate, or High
                Interaction Risk: Low, Moderate, or High
                Adherence Risk: Low, Moderate, or High

                Use plain text only. Do not include raw markdown symbols such as ###, *, or other markdown formatting.
                Always include a Prediction Analysis section with exact risk lines.
                Format the response with clear headings and bullet lists where appropriate.
                """

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                result = response.text
                structured_result = parse_medication_response(result)


            else:

                valid_images = []

                for file in uploaded_files:
                    if file and file.filename:
                        try:
                            img = Image.open(file.stream)
                            valid_images.append(img)
                        except Exception:
                            error = "Unable to open one of the uploaded images. Please try a different file."
                            break

                if not error and len(valid_images) < 1:
                    error = "Please upload at least 1 image or enter a medication name."

                elif not error and len(valid_images) > 3:
                    error = "Maximum of 3 images allowed."

                elif not error:

                    prompt = """
                    Analyze these medication images.

                    Identify:
                    - Medication Name
                    - Purpose
                    - Active Ingredients
                    - Typical Dosage
                    - Possible Side Effects
                    - Warnings
                    - Drug Interactions
                    - Expiration Information if visible

                    Prediction Analysis:
                    Side Effect Risk: Low, Moderate, or High
                    Interaction Risk: Low, Moderate, or High
                    Adherence Risk: Low, Moderate, or High

                    Use plain text only. Do not include raw markdown symbols such as ###, *, or other markdown formatting.
                    Always include a Prediction Analysis section with exact risk lines.
                    Format the response with clear headings and bullet lists where appropriate.
                    """

                    contents = [prompt]

                    for img in valid_images:
                        contents.append(img)

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents
                    )

                    result = response.text
                    structured_result = parse_medication_response(result)

        except Exception as e:

            error = str(e)

            print("\nGEMINI ERROR:")
            print(e)

    return render_template(
        "index.html",
        result=result,
        structured_result=structured_result,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
