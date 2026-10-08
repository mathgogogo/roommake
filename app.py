import io
import random
from PIL import Image, ImageDraw, ImageFont
import streamlit as st


# 1. txt 파일 내용 파싱 함수
def parse_txt(content_str):
    room_capacity = {}
    students = []
    current_section = None

    lines = content_str.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == "[방정원]":
            current_section = "room"
            continue
        elif line == "[학생명단]":
            current_section = "student"
            continue

        if current_section == "room" and ":" in line:
            room_name, cap = line.split(":")
            room_capacity[room_name.strip()] = int(cap.strip())
        elif current_section == "student":
            students.append(line)

    return room_capacity, students


# 2. 랜덤 방 배정 함수
def assign_rooms(room_capacity, students):
    shuffled_students = students.copy()
    random.shuffle(shuffled_students)

    assignments = {room: [] for room in room_capacity.keys()}
    student_idx = 0
    total_students = len(students)

    for room, capacity in room_capacity.items():
        for _ in range(capacity):
            if student_idx < total_students:
                assignments[room].append(shuffled_students[student_idx])
                student_idx += 1

    return assignments


# 3. 이미지 생성 함수
def generate_assignment_image(assignments):
    num_rooms = len(assignments)
    card_width, card_height, padding = 240, 200, 20
    cols = min(3, max(1, num_rooms))
    rows = (num_rooms + cols - 1) // cols

    img_width = cols * (card_width + padding) + padding
    img_height = rows * (card_height + padding) + padding + 60

    image = Image.new("RGB", (img_width, img_height), color="#F4F6F9")
    draw = ImageDraw.Draw(image)

    try:
        font_title = ImageFont.truetype("malgun.ttf", 24)
        font_room = ImageFont.truetype("malgun.ttf", 18)
        font_text = ImageFont.truetype("malgun.ttf", 15)
    except IOError:
        font_title = font_room = font_text = ImageFont.load_default()

    draw.text((padding, 15), "🚌 수학여행 방 배정 결과", fill="#2C3E50", font=font_title)

    for idx, (room, members) in enumerate(assignments.items()):
        r, c = idx // cols, idx % cols
        x1 = padding + c * (card_width + padding)
        y1 = 70 + r * (card_height + padding)
        x2, y2 = x1 + card_width, y1 + card_height

        draw.rounded_rectangle(
            [x1, y1, x2, y2], radius=10, fill="white", outline="#DCDFE6", width=2
        )
        draw.rounded_rectangle(
            [x1, y1, x2, y1 + 40],
            radius=10,
            fill="#3498DB",
            corners=(True, True, False, False),
        )
        draw.text((x1 + 15, y1 + 10), room, fill="white", font=font_room)

        member_text = (
            "\n".join([f"• {m}" for m in members]) if members else "(빈 방)"
        )
        draw.text(
            (x1 + 20, y1 + 55),
            member_text,
            fill="#333333",
            font=font_text,
            spacing=8,
        )

    return image


# --- Streamlit 웹 화면 구성 ---
st.title("🎲 수학여행 방 배정 프로그램")
st.write("방 정원과 명단이 적힌 `.txt` 파일을 업로드하면 자동으로 배정표 이미지를 만들어 드립니다.")

# 파일 업로드 위젯
uploaded_file = st.file_uploader(
    "txt 파일을 선택하세요", type=["txt"]
)

if uploaded_file is not None:
    # 파일 읽기
    content = uploaded_file.read().decode("utf-8")
    room_cap, student_list = parse_txt(content)

    if st.button("🎲 방 다시 배정하기"):
        # 배정 및 이미지 생성
        result = assign_rooms(room_cap, student_list)
        result_img = generate_assignment_image(result)

        # 화면에 이미지 표시
        st.image(result_img, caption="방 배정 결과", use_column_width=True)

        # 이미지 다운로드 버튼
        buf = io.BytesIO()
        result_img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="📥 배정 결과 이미지 다운로드",
            data=byte_im,
            file_name="수학여행_방배정_결과.png",
            mime="image/png",
        )