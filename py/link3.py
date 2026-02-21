from manim import *

class ColoredLinkedList(Scene):
    def construct(self):
        # 数据和节点颜色（根据你的示例图）
        values = [1, 4, 3, 2, 5, 2]
        colors = [YELLOW, RED, RED, YELLOW, RED, YELLOW]

        nodes = []
        dots = []
        arrows = []

        node_width = 1.2
        node_height = 0.8
        spacing = 2.3

        # 1️⃣ 创建节点、数字和出口圆点
        for i, (val, color) in enumerate(zip(values, colors)):
            rect = RoundedRectangle(
                width=node_width,
                height=node_height,
                corner_radius=0.1,
                fill_color=color,
                fill_opacity=1,
                stroke_color=BLACK,
                stroke_width=2
            )
            rect.move_to(RIGHT * i * spacing)

            label = Text(str(val), font_size=32).move_to(rect.get_center())

            # 出口小圆点
            dot = Circle(radius=0.08, fill_color=WHITE, fill_opacity=1, stroke_color=BLACK, stroke_width=1)
            dot_radius = 0.08
            dot.move_to(rect.get_center() + RIGHT * (node_width / 2 - dot_radius))

            dot.next_to(rect, RIGHT, buff=0)

            self.add(rect, label, dot)

            nodes.append(rect)
            dots.append(dot)

        # 2️⃣ 创建箭头指向下一个节点
        for i in range(len(nodes) - 1):
            arrow = Arrow(
                start=dots[i].get_right(),
                end=nodes[i + 1].get_left(),
                buff=0.05,
                stroke_width=5,
                color=GRAY
            )
            arrows.append(arrow)
            self.add(arrow)

        # 3️⃣ 最后一个箭头指向 null
        null_text = Text("null", font_size=28)
        last_arrow = Arrow(
            start=dots[-1].get_right(),
            end=dots[-1].get_right() + RIGHT * 0.8,
            buff=0,
            stroke_width=5,
            color=GRAY
        )
        null_text.next_to(last_arrow.get_end(), RIGHT, buff=0.1)
        self.add(last_arrow, null_text)

        # 4️⃣ 居中整体
        all_items = VGroup(*nodes, *dots, *arrows, last_arrow, null_text)
        all_items.move_to(ORIGIN)
