# -*- coding: utf-8 -*-
import math, os

FONT = "Noto Sans CJK SC, Droid Sans Fallback, sans-serif"
OUT = "/home/chen/campus_market/resource"
os.makedirs(OUT, exist_ok=True)

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))

def norm(v):
    L = math.hypot(v[0], v[1])
    return (v[0]/L, v[1]/L) if L else (0, 0)

def perp(d):
    return (-d[1], d[0])

def text(x, y, s, size=20, anchor="start", weight="normal",
         fill="#222", rot=None, halo=False, family=FONT):
    extra = ""
    if rot is not None:
        extra = f' transform="rotate({rot} {x} {y})"'
    if halo:
        extra += ' paint-order="stroke" stroke="#ffffff" stroke-width="8" stroke-linejoin="round"'
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}"{extra}>{esc(s)}</text>')

def rect(x, y, w, h, fill, stroke, rx=14, sw=2.5):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def shadow(x, y, w, h, rx=14):
    return (f'<rect x="{x+7}" y="{y+9}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="#000000" opacity="0.07"/>')

def path(pts, color="#3d3d3d", width=2.6, dashed=False):
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    dash = ' stroke-dasharray="4 10" stroke-linecap="round"' if dashed else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash}/>'

def crow(P, d, color="#3d3d3d"):
    d = norm(d); p = perp(d)
    Q = (P[0] - d[0]*18, P[1] - d[1]*18)
    A = (P[0] + p[0]*12, P[1] + p[1]*12)
    B = (P[0] - p[0]*12, P[1] - p[1]*12)
    out = [path([Q, P], color), path([Q, A], color), path([Q, B], color)]
    return Q, "".join(out)

def tick(P, d, color="#3d3d3d"):
    d = norm(d); p = perp(d)
    C = (P[0] - d[0]*26, P[1] - d[1]*26)
    A = (C[0] + p[0]*12, C[1] + p[1]*12)
    B = (C[0] - p[0]*12, C[1] - p[1]*12)
    return path([A, B], color, 2.6)

def arrow(P, d, color="#3d3d3d"):
    d = norm(d); p = perp(d)
    B = (P[0] - d[0]*20, P[1] - d[1]*20)
    A = (B[0] + p[0]*9,  B[1] + p[1]*9)
    C = (B[0] - p[0]*9,  B[1] - p[1]*9)
    return path([A, P], color, 2.4) + path([C, P], color, 2.4)

def edge(pts, many=None, one=None, dashed=False, arrow_end=None, color="#3d3d3d", width=2.6):
    pts = [tuple(p) for p in pts]
    out = []
    many_fork = None
    # many end: shorten main line, draw fork
    if many in (0, -1):
        i = 0 if many == 0 else len(pts) - 1
        j = 1 if i == 0 else len(pts) - 2
        P = pts[i]
        d = norm((P[0]-pts[j][0], P[1]-pts[j][1]))
        Q, fork = crow(P, d, color)
        pts[i] = Q
        many_fork = fork
    # one end tick
    one_tick = ""
    if one in (0, -1):
        i = 0 if one == 0 else len(pts) - 1
        j = 1 if i == 0 else len(pts) - 2
        P = pts[i]
        d = norm((P[0]-pts[j][0], P[1]-pts[j][1]))
        one_tick = tick(P, d, color)
    arr = ""
    if arrow_end in (0, -1):
        i = 0 if arrow_end == 0 else len(pts) - 1
        j = 1 if i == 0 else len(pts) - 2
        P = pts[i]
        d = norm((P[0]-pts[j][0], P[1]-pts[j][1]))
        arr = arrow(P, d, color)
    out.append(path(pts, color, width, dashed))
    if many_fork: out.append(many_fork)
    if one_tick: out.append(one_tick)
    if arr: out.append(arr)
    return "".join(out)

def table(x, y, w, title, rows, header, body, stroke, field_w=200, type_w=150, key_w=60):
    header_h, row_h, pad = 60, 50, 18
    h = header_h + row_h * len(rows)
    out = [shadow(x, y, w, h)]
    out.append(rect(x, y, w, h, body, stroke))
    # header band with rounded top corners
    r = 14
    out.append(f'<path d="M {x} {y+header_h} L {x} {y+r} Q {x} {y} {x+r} {y} '
               f'L {x+w-r} {y} Q {x+w} {y} {x+w} {y+r} L {x+w} {y+header_h} Z" '
               f'fill="{header}" stroke="{stroke}" stroke-width="2.5"/>')
    cx = x + w/2
    out.append(text(cx, y + header_h/2 + 2, title, 24, "middle", "bold", "#1f1f1f"))
    # column separators
    xs = [x + pad + field_w, x + pad + field_w + type_w,
          x + pad + field_w + type_w + key_w]
    for xv in xs:
        out.append(f'<line x1="{xv}" y1="{y+header_h}" x2="{xv}" y2="{y+h}" stroke="{stroke}" stroke-width="1" opacity="0.35"/>')
    # row separators
    for i in range(1, len(rows)):
        yy = y + header_h + i*row_h
        out.append(f'<line x1="{x}" y1="{yy}" x2="{x+w}" y2="{yy}" stroke="{stroke}" stroke-width="1" opacity="0.35"/>')
    key_colors = {"PK": "#B26A00", "FK": "#2F6FB2", "UQ": "#7A4FA3"}
    for i, (name, typ, key, desc) in enumerate(rows):
        cy = y + header_h + i*row_h + row_h/2 + 2
        name_color = "#222" if not name.startswith("(") else "#666"
        out.append(text(x+pad, cy, name, 20, "start", "bold" if key == "PK" else "normal", name_color))
        out.append(text(x+pad+field_w, cy, typ, 19, "start", "normal", "#444"))
        if key:
            out.append(text(x+pad+field_w+type_w+22, cy, key, 18, "middle", "bold",
                            key_colors.get(key, "#666")))
        out.append(text(x+pad+field_w+type_w+key_w, cy, desc, 19, "start", "normal", "#333"))
    return "".join(out), h

def svg_page(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#ffffff"/>'
            f'{body}</svg>')

# ---------------- ER diagram ----------------
W, H = 2800, 2080
C_USERS   = ("#EFD9F5", "#FBF4FD", "#B07CC6")
C_ITEMS   = ("#CCEFEA", "#EDF9F7", "#4FB3A9")
C_MSG     = ("#FFE3C6", "#FFF7EE", "#E0A163")
C_FAV     = ("#D3E6F8", "#F0F7FD", "#6FA8DC")
C_ORDER   = ("#D8EDD3", "#F3FAF0", "#7AB86C")
C_REPORT  = ("#F8D6D6", "#FDF0F0", "#CF7B7B")

body = []
def add(s): body.append(s)

users_rows = [
 ("id","INT","PK","主键"),
 ("student_id","VARCHAR(20)","UQ","学号（登录账号）"),
 ("password","VARCHAR(255)","","密码（加密存储）"),
 ("phone","VARCHAR(20)","","手机号"),
 ("role","INT","","0=学生 1=管理员"),
 ("status","INT","","1=正常 0=封禁"),
 ("created_at","DATETIME","","注册时间"),
]
items_rows = [
 ("id","INT","PK","主键"),
 ("user_id","INT","FK","发布者"),
 ("title","VARCHAR(100)","","标题"),
 ("description","TEXT","","商品描述"),
 ("type","INT","","1=出售 2=求购 3=交换"),
 ("price","DECIMAL(10,2)","","期望价格"),
 ("image_urls","VARCHAR(500)","","图片 URL（多图）"),
 ("status","INT","","0=待审核 1=展示 2=驳回 3=下架"),
 ("reject_reason","VARCHAR(255)","","驳回原因"),
 ("created_at","DATETIME","","发布时间"),
]
msg_rows = [
 ("id","INT","PK","主键"),
 ("item_id","INT","FK","所属商品"),
 ("user_id","INT","FK","留言者"),
 ("content","VARCHAR(500)","","留言内容"),
 ("created_at","DATETIME","","留言时间"),
]
fav_rows = [
 ("id","INT","PK","主键"),
 ("user_id","INT","FK","收藏者"),
 ("item_id","INT","FK","商品"),
 ("created_at","DATETIME","","收藏时间"),
 ("(联合约束)","—","UQ","Unique(user_id,item_id)"),
]
order_rows = [
 ("id","INT","PK","主键"),
 ("item_id","INT","FK","商品"),
 ("buyer_id","INT","FK","买家"),
 ("seller_id","INT","FK","卖家"),
 ("status","INT","","0=待确认 1=交易中 2=完成 3=取消"),
 ("created_at","DATETIME","","创建时间"),
 ("(业务规则)","—","","同一商品仅一条活跃订单"),
]
report_rows = [
 ("id","INT","PK","主键"),
 ("reporter_id","INT","FK","举报人"),
 ("target_type","INT","","1=商品 2=用户"),
 ("target_id","INT","","被举报对象 ID（多态）"),
 ("reason","VARCHAR(255)","","举报原因"),
 ("status","INT","","0=待处理 1=属实 2=不属实"),
 ("handler_id","INT","FK","处理管理员"),
 ("handle_note","VARCHAR(255)","","处理备注"),
 ("created_at","DATETIME","","举报时间"),
 ("handled_at","DATETIME","","处理时间"),
]

t_users   = (920, 60,  780)
t_items   = (60,  680, 840)
t_reports = (1660,680, 900)
t_msgs    = (40,  1560,680)
t_favs    = (740, 1560,720)
t_orders  = (1520,1560,840)

for (x,y,w), title, rows, cols in [
    (t_users,   "USERS",    users_rows,  C_USERS),
    (t_items,   "ITEMS",    items_rows,  C_ITEMS),
    (t_reports, "REPORTS",  report_rows, C_REPORT),
    (t_msgs,    "MESSAGES", msg_rows,    C_MSG),
    (t_favs,    "FAVORITES",fav_rows,    C_FAV),
    (t_orders,  "ORDERS",   order_rows,  C_ORDER),
]:
    s, _ = table(x, y, w, title, rows, *cols)
    add(s)

# edges
add(edge([(1100,470),(1100,590),(300,590),(300,680)], one=0, many=-1))
add(edge([(920,260),(20,260),(20,1470),(200,1470),(200,1560)], one=0, many=-1))
add(edge([(380,1240),(380,1560)], one=0, many=-1))
add(edge([(740,1240),(740,1450),(1100,1450),(1100,1560)], one=0, many=-1))
add(edge([(1350,470),(1350,1560)], one=0, many=-1))
add(edge([(1700,340),(2700,340),(2700,1800),(2360,1800)], one=0, many=-1))
add(edge([(1600,470),(1600,620),(1800,620),(1800,680)], one=0, many=-1))
add(edge([(1660,900),(900,900)], dashed=True, arrow_end=-1))
add(edge([(900,1150),(1300,1150),(1300,1420),(1520,1420),(1520,1560)], one=0, many=-1))

# edge labels
for s in [
    text(650,585,"发布",22,"middle",halo=True),
    text(26,1442,"留言",22,"start",halo=True),
    text(425,1412,"包含",22,"start",halo=True),
    text(930,1435,"被收藏",22,"middle",halo=True),
    text(1390,1010,"收藏",22,"start",halo=True),
    text(2732,1100,"买入 / 卖出",22,"middle",rot=-90,halo=True),
    text(1620,602,"提交 / 处理",22,"start",halo=True),
    text(1280,878,"指向（多态）",22,"middle",halo=True),
    text(960,1132,"产生",22,"start",halo=True),
]:
    add(s)
# cardinality labels
for x,y,s in [
    (1125,505,"1"),(325,660,"N"),
    (893,285,"1"),(225,1535,"N"),
    (405,1268,"1"),(405,1532,"N"),
    (765,1268,"1"),(1125,1532,"N"),
    (1375,505,"1"),(1375,1532,"N"),
    (1725,368,"1"),(2390,1778,"N"),
    (1625,500,"1"),(1825,658,"N"),
    (925,1178,"1"),(1545,1532,"N"),
]:
    add(text(x,y,s,19,"middle","normal","#5c5c5c",halo=True))

er_svg = svg_page(W, H, "".join(body))
open(os.path.join(OUT,"ER.svg"),"w",encoding="utf-8").write(er_svg)

# ---------------- UML diagram ----------------
W2, H2 = 2500, 2620
U_AUDIT = ("#D8E9F8", "#6FA8DC")
U_USER  = ("#F1DDF2", "#B07CC6")
U_ITEM  = ("#D6F1EC", "#4FB3A9")
U_REP   = ("#F8DCD8", "#CF7B7B")
U_ORD   = ("#E1F1D8", "#7AB86C")

body2 = []
def add2(s): body2.append(s)

def uml_class(x, y, w, name, attrs, methods, header, stroke):
    header_h, line_h, pad = 60, 34, 20
    h_attr = (len(attrs)*line_h + 2*pad) if attrs else 0
    h_meth = (len(methods)*line_h + 2*pad) if methods else 0
    h = header_h + h_attr + h_meth
    out = [shadow(x, y, w, h)]
    out.append(rect(x, y, w, h, "#ffffff", stroke))
    r = 14
    out.append(f'<path d="M {x} {y+header_h} L {x} {y+r} Q {x} {y} {x+r} {y} '
               f'L {x+w-r} {y} Q {x+w} {y} {x+w} {y+r} L {x+w} {y+header_h} Z" '
               f'fill="{header}" stroke="{stroke}" stroke-width="2.5"/>')
    out.append(text(x+w/2, y+header_h/2+2, name, 24, "middle", "bold", "#161616"))
    yy = y + header_h
    if attrs:
        out.append(f'<line x1="{x}" y1="{yy}" x2="{x+w}" y2="{yy}" stroke="{stroke}" stroke-width="1.6"/>')
        for a in attrs:
            yy += line_h
            out.append(text(x+pad, yy - line_h/2 + 2, a, 20, "start", "normal", "#2b2b2b"))
        yy = y + header_h + h_attr
        out.append(f'<line x1="{x}" y1="{yy}" x2="{x+w}" y2="{yy}" stroke="{stroke}" stroke-width="1.6"/>')
    for m in methods:
        yy += line_h
        out.append(text(x+pad, yy - line_h/2 + 2, m, 20, "start", "normal", "#2b2b2b"))
    return "".join(out), h

audit_attrs = []
audit_methods = ["+approve_item(item_id)", "+reject_item(item_id, reason)",
                 "+ban_user(user_id)", "+handle_report(report_id, status, note)"]
user_attrs = ["+user_id: int","+student_id: str","+password: str","+phone: str",
              "+role: int","+status: int"]
user_methods = ["+login()","+update_profile()","+verify_token()"]
item_attrs = ["+item_id: int","+user_id: int","+title: str","+type: int","+price: Decimal",
              "+image_urls: str","+status: int","+reject_reason: str"]
item_methods = ["+create_item()","+update_item()","+off_shelf()"]
report_attrs = ["+report_id: int","+reporter_id: int","+target_type: int","+target_id: int",
                "+reason: str","+status: int","+handler_id: int"]
report_methods = ["+create_report()","+get_pending_reports()"]
order_attrs = ["+order_id: int","+item_id: int","+buyer_id: int","+seller_id: int","+status: int"]
order_methods = ["+create_order()","+confirm_trade()","+cancel_order()"]

for (x,y,w), name, attrs, meths, cols in [
    ((760,60,720),  "AuditService", audit_attrs, audit_methods, U_AUDIT),
    ((1320,420,600),"User",         user_attrs,  user_methods,  U_USER),
    ((80,820,640),  "Item",         item_attrs,  item_methods,  U_ITEM),
    ((1000,1500,640),"Report",      report_attrs,report_methods,U_REP),
    ((1000,2180,600),"Order",       order_attrs, order_methods, U_ORD),
]:
    s, _ = uml_class(x, y, w, name, attrs, meths, *cols)
    add2(s)

# associations
add2(edge([(1320,620),(760,620),(760,760),(520,760),(520,820)], one=0, many=-1))
add2(edge([(1500,826),(1500,1500)], one=0, many=-1))
add2(edge([(1920,700),(2380,700),(2380,2400),(1600,2400)], one=0, many=-1))
add2(edge([(300,1294),(300,2400),(1000,2400)], one=0, many=-1))
# dependencies
add2(edge([(900,276),(900,740),(400,740),(400,820)], dashed=True, arrow_end=-1))
add2(edge([(1480,140),(2050,140),(2050,520),(1920,520)], dashed=True, arrow_end=-1))
add2(edge([(1200,276),(1200,1500)], dashed=True, arrow_end=-1))
add2(edge([(1000,1700),(860,1700),(860,1150),(720,1150)], dashed=True, arrow_end=-1))

for s in [
    text(1000,598,"发布",22,"middle",halo=True),
    text(1530,1150,"提交",22,"start",halo=True),
    text(2410,1500,"买入 / 卖出",22,"middle",rot=-90,halo=True),
    text(650,2378,"产生",22,"middle",halo=True),
    text(650,716,"审核依赖",22,"middle",halo=True),
    text(1760,116,"封禁依赖",22,"middle",halo=True),
    text(1176,900,"处理举报依赖",22,"middle",rot=-90,halo=True),
    text(836,1430,"指向（多态）",22,"middle",rot=-90,halo=True),
]:
    add2(s)
for x,y,s in [
    (1295,650,"1"),(545,795,"*"),
    (1525,855,"1"),(1525,1475,"*"),
    (1945,725,"1"),(1615,2378,"*"),
    (325,1320,"1"),(975,2378,"*"),
]:
    add2(text(x,y,s,19,"middle","normal","#5c5c5c",halo=True))

uml_svg = svg_page(W2, H2, "".join(body2))
open(os.path.join(OUT,"UML.svg"),"w",encoding="utf-8").write(uml_svg)

def html(svg, w, h):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>'
            f'html,body{{margin:0;padding:0;background:#fff}}svg{{display:block}}'
            f'</style></head><body>{svg}</body></html>')

open("/tmp/diagrams_build/ER.html","w",encoding="utf-8").write(html(er_svg, W, H))
open("/tmp/diagrams_build/UML.html","w",encoding="utf-8").write(html(uml_svg, W2, H2))
print("svgs written", W, H, W2, H2)
