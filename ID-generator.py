import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import pandas as pd
import uuid

st.set_page_config(layout="centered", page_title="ID Card Generator")

# Set white background
st.markdown("""
    <style>
        .stApp {
            background-color: grey;
        }
    </style>
""", unsafe_allow_html=True)


st.image("kreeda.png", width=150)  # Adjust width as needed
st.title("🆔 ID Card Generator")

# Inputs
name = st.text_input("Enter Full Name")
dob = st.date_input("Date of Birth")
address = st.text_area("Enter Address")
mobile = st.text_input("Enter Mobile Number")
sport = st.selectbox("Select Interested Sport", ["Cricket", "Football", "Volleyball"])
photo = st.file_uploader("Upload Your Photo", type=["png", "jpg", "jpeg"])

# Contest and QR section
contest = st.selectbox("Select Contest", ["--Select--", "Football Championship", "Volleyball Challenge", "Cricket League"])
qr_images = {
    "Football Championship": "football_qr.jpg",
    "Volleyball Challenge": "volleyball_qr.jpg",
    "Cricket League": "cricket_qr.jpg"
}

payment_done = False
if contest != "--Select--":
    st.info(f"Please scan the QR below to pay for the {contest}")
    qr_path = qr_images.get(contest)
    if qr_path and os.path.exists(qr_path):
        st.image(qr_path, caption="Scan to Pay", width=250)
        payment_done = st.checkbox("✅ I have completed the payment")
    else:
        st.error("QR code not found for selected contest.")

# Directories and file paths
photo_dir = "photos"
csv_file = "id_card_data.csv"
template_path = "id.png"  # Your uploaded background

# Ensure photo directory and CSV exist
os.makedirs(photo_dir, exist_ok=True)
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=["Name", "Date of Birth", "Address", "Mobile Number", "Sport", "Contest", "Photo"])
    df.to_csv(csv_file, index=False)

# Generate ID card
if st.button("Generate ID Card"):
    if name and dob and address and mobile and photo is not None and contest != "--Select--" and payment_done:
        # Save uploaded photo
        unique_filename = f"{uuid.uuid4().hex}_{photo.name}"
        photo_path = os.path.join(photo_dir, unique_filename)
        with open(photo_path, "wb") as f:
            f.write(photo.read())

        # Load ID card background
        try:
            card_bg = Image.open(template_path).convert("RGBA")
        except FileNotFoundError:
            st.error("Background template image not found. Make sure 'id.png' is in the same directory.")
            st.stop()

        # Resize template if needed
        card_bg = card_bg.resize((400, 550))

        # Paste user photo
        user_photo = Image.open(photo_path).resize((120, 120)).convert("RGBA")
        card_bg.paste(user_photo, (130, 150), user_photo)

        # Draw text on top
        draw = ImageDraw.Draw(card_bg)
        try:
            font_bold = ImageFont.truetype("arialbd.ttf", 20)
            font_regular = ImageFont.truetype("arial.ttf", 16)
        except:
            font_bold = ImageFont.load_default()
            font_regular = ImageFont.load_default()

        # Center-aligned name
        text_width = draw.textlength(name.upper(), font=font_bold)
        x_position = (card_bg.width - text_width) // 2
        draw.text((x_position, 300), name.upper(), fill="black", font=font_bold)

        # Other fields
        draw.text((120, 345), f"    {dob.strftime('%d-%m-%Y')}", fill="black", font=font_regular)
        draw.text((120, 385), f"    {mobile}", fill="black", font=font_regular)
        draw.text((175, 423), f"    {sport}", fill="black", font=font_regular)
        draw.text((120, 463), f"    {address}", fill="black", font=font_regular)

        # Show ID card
        st.image(card_bg)

        # Save ID card to memory for download
        img_bytes = io.BytesIO()
        card_bg.save(img_bytes, format='PNG')
        st.download_button("Download ID Card", img_bytes.getvalue(), file_name="id_card.png", mime="image/png")

        # Save details to CSV
        new_entry = pd.DataFrame([[name, dob, address, mobile, sport, contest, photo_path]],
                                 columns=["Name", "Date of Birth", "Address", "Mobile Number", "Sport", "Contest", "Photo"])
        new_entry.to_csv(csv_file, mode='a', header=False, index=False)

        st.success("✅ ID card created and saved successfully.")
    else:
        st.warning("⚠️ Please complete all fields, select a contest, and confirm your payment.")
