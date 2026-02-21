from manim import *

class NodeArrowDemoPointer(Scene):
    def construct(self):
        nodes = []
        labels = []
        arrows = []

        node_width = 1.4
        node_height = 0.8
        spacing = 2.3  # 节点间距
        node_count = 5

        # 1️⃣ 创建节点和标签
        for i in range(node_count):
            rect = RoundedRectangle(
                width=node_width,
                height=node_height,
                corner_radius=0.12,
                stroke_color=BLUE,
                fill_opacity=0
            )
            rect.move_to(RIGHT * i * spacing)

            label = Text(str(i + 1), font_size=30)
            label.move_to(rect.get_center())
            label.set_z_index(1)

            nodes.append(rect)
            labels.append(label)

        # 2️⃣ 创建节点间箭头
        for i in range(node_count - 1):
            arrow = Arrow(
                nodes[i].get_right(),
                nodes[i + 1].get_left(),
                buff=0.02,
                stroke_width=6,
                color=BLUE,
                max_tip_length_to_length_ratio=0.25
            )
            arrows.append(arrow)

        # 3️⃣ 把节点、标签、箭头整体居中
        all_items = VGroup(*nodes, *labels, *arrows)
        all_items.move_to(ORIGIN)

        # 4️⃣ 一次性显示节点、标签、箭头（静态，无动画）
        self.add(*nodes)
        self.add(*labels)
        self.add(*arrows)

        # 5️⃣ 创建遍历指针（初始在第一个节点下方）
        pointer = Arrow(
            start=DOWN * 1.6,    # 指针长度加大
            end=ORIGIN,
            color=GOLD_D,
            stroke_width=8,       # 指针更粗
            max_tip_length_to_length_ratio=0.4
        )
        pointer.next_to(nodes[0], DOWN, buff=0.15)
        self.add(pointer)  # 指针出现

        # 6️⃣ 指针依次滑动到每个节点
        for i in range(1, node_count):
            self.play(
                pointer.animate.next_to(nodes[i], DOWN, buff=0.15),
                run_time=1.0  # 🔹 调慢滑动速度，默认 0.6 太快
            )

        self.wait(1)
