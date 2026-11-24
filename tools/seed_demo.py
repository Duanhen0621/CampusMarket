"""Seed demo data for the campus market project.

Prerequisites:
- backend running at 127.0.0.1:8000
- admin account 20260000/20260000 already exists
- database has no conflicting demo data

Run:
    cd backend && .venv/bin/python ../tools/seed_demo.py
"""

import json
import os
import subprocess
import urllib.error
import urllib.request

from PIL import Image, ImageDraw, ImageFont

BASE = "http://127.0.0.1:8000/api/v1"
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
IMG_DIR = "/tmp/demo_imgs"
os.makedirs(IMG_DIR, exist_ok=True)


def call(method, path, token=None, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"{method} {path} -> {exc.code} {exc.read().decode('utf-8')}"
        ) from None


def login(student_id):
    res = call(
        "POST",
        "/auth/login",
        body={"student_id": student_id, "password": student_id},
    )
    return res["data"]["access_token"]


def make_image(title, subtitle, color, path):
    width, height = 1000, 750
    top = tuple(min(255, c + 45) for c in color)
    bottom = tuple(max(0, c - 40) for c in color)
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / height
        draw.line(
            [(0, y), (width, y)],
            fill=tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)),
        )
    draw.rounded_rectangle(
        [70, height // 2 - 150, width - 70, height // 2 + 150],
        radius=36,
        fill=(255, 255, 255),
    )
    title_font = ImageFont.truetype(FONT_PATH, 60)
    sub_font = ImageFont.truetype(FONT_PATH, 30)
    bbox = draw.textbbox((0, 0), title, font=title_font)
    draw.text(
        ((width - (bbox[2] - bbox[0])) / 2, height // 2 - 110),
        title,
        font=title_font,
        fill="#1f2329",
    )
    bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
    draw.text(
        ((width - (bbox[2] - bbox[0])) / 2, height // 2 + 30),
        subtitle,
        font=sub_font,
        fill="#6b7280",
    )
    image.save(path, "JPEG", quality=88)


def upload(path, token):
    result = subprocess.run(
        [
            "curl", "-sS", "-X", "POST", BASE + "/uploads/image",
            "-H", "Authorization: Bearer " + token,
            "-F", f"file=@{path};type=image/jpeg",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    res = json.loads(result.stdout)
    if "data" not in res:
        raise RuntimeError(result.stdout)
    return res["data"]["url"]


tokens = {
    "u1": login("20260001"),
    "u2": login("20260002"),
    "u3": login("20260003"),
    "admin": login("20260000"),
}

items_spec = [
    ("bike", "u1", "九成新山地自行车", "毕业出，可小刀，周末可看车", 1, 150,
     (64, 120, 190), "山地车 · 九成新"),
    ("keyboard", "u2", "机械键盘 87 键", "红轴，手感很好，带原装线", 1, 120,
     (120, 90, 180), "87 键 · 红轴"),
    ("math", "u3", "高等数学教材（第七版）", "上下册，有少量笔记", 1, 20,
     (70, 150, 110), "教材 · 少量笔记"),
    ("fridge", "u1", "求购：宿舍小冰箱", "求一个小冰箱，能制冷即可", 2, None,
     (60, 160, 190), "求购 · 预算面议"),
    ("tent", "u2", "交换：露营帐篷", "双人帐篷，想换插线板或台灯", 3, None,
     (220, 140, 70), "交换 · 双人帐篷"),
    ("basketball", "u3", "篮球（斯伯丁）", "打了几次，气足", 1, 60,
     (170, 110, 60), "篮球 · 九成新"),
    ("earbuds", "u2", "蓝牙耳机（待审核）", "半入耳式，续航不错", 1, 80,
     (120, 125, 135), "待审核示例"),
    ("essay", "u3", "代写作业服务（违规示例）", "示例：此类内容会被管理员驳回", 1, 50,
     (190, 90, 90), "违规示例"),
    ("vocab", "u2", "四级词汇书（已售出）", "已通过订单完成交易", 1, 15,
     (200, 180, 80), "已售出示例"),
]

item_ids = {}
for key, owner, title, desc, type_, price, color, sub in items_spec:
    image_path = os.path.join(IMG_DIR, f"{key}.jpg")
    make_image(title, sub, color, image_path)
    url = upload(image_path, tokens[owner])
    res = call(
        "POST",
        "/items",
        tokens[owner],
        {
            "title": title,
            "description": desc,
            "type": type_,
            "price": price,
            "image_urls": [url],
        },
    )
    item_ids[key] = res["data"]["item_id"]

# 审核：1-6 和已售出示例通过，违规示例驳回，耳机保持待审核
approved = ["bike", "keyboard", "math", "fridge", "tent", "basketball", "vocab"]
for key in approved:
    call("PUT", f"/admin/items/{item_ids[key]}/audit", tokens["admin"], {"status": 1})
call(
    "PUT",
    f"/admin/items/{item_ids['essay']}/audit",
    tokens["admin"],
    {"status": 2, "reason": "平台禁止发布代写、违规服务类内容"},
)

messages = [
    ("bike", "u2", "同学你好，车子还在吗？周末能看车吗？"),
    ("bike", "u1", "在的，周六下午可以。"),
    ("keyboard", "u3", "键盘是什么轴？"),
    ("keyboard", "u2", "红轴，手感很好。"),
    ("basketball", "u1", "篮球还在吗？"),
]
for key, user, content in messages:
    call(
        "POST",
        f"/items/{item_ids[key]}/messages",
        tokens[user],
        {"content": content},
    )

for key, user in [("bike", "u2"), ("math", "u3"), ("tent", "u1")]:
    call("POST", f"/items/{item_ids[key]}/favorite", tokens[user])

# 已完成订单：u2 卖，u3 买
order = call(
    "POST", "/orders", tokens["u3"], {"item_id": item_ids["vocab"]}
)["data"]["order_id"]
call("PUT", f"/orders/{order}/status", tokens["u2"], {"status": 1})
call("PUT", f"/orders/{order}/status", tokens["u3"], {"status": 2})

# 待确认订单
call("POST", "/orders", tokens["u3"], {"item_id": item_ids["bike"]})

# 求购订单：u1 发布求购，u2 响应，u2 是卖家
order_want = call(
    "POST", "/orders", tokens["u2"], {"item_id": item_ids["fridge"]}
)["data"]["order_id"]
call("PUT", f"/orders/{order_want}/status", tokens["u2"], {"status": 1})

# 已取消订单
order_tent = call(
    "POST", "/orders", tokens["u3"], {"item_id": item_ids["tent"]}
)["data"]["order_id"]
call("PUT", f"/orders/{order_tent}/status", tokens["u3"], {"status": 3})

# 举报：两条待处理，一条已处理
call(
    "POST",
    "/reports",
    tokens["u2"],
    {"target_type": 1, "target_id": item_ids["math"], "reason": "商品描述与实际不符，有大量缺页"},
)
call(
    "POST",
    "/reports",
    tokens["u3"],
    {"target_type": 2, "target_id": 4, "reason": "交易沟通中态度恶劣"},
)
report_done = call(
    "POST",
    "/reports",
    tokens["u1"],
    {"target_type": 1, "target_id": item_ids["essay"], "reason": "发布违规服务内容"},
)["data"]["report_id"]
call(
    "PUT",
    f"/admin/reports/{report_done}",
    tokens["admin"],
    {"status": 1, "handle_note": "已核实，商品已驳回"},
)

print("items:", item_ids)
print("orders:", {"completed": order, "want": order_want, "cancelled": order_tent})
print("reports handled:", report_done)
