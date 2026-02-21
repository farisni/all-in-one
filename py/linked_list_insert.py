from manim import *

class NodeArrowDemo(Scene):
    def construct(self):
        nodes = []
        labels = []
        arrows = []

        node_width = 1.4
        node_height = 0.8
        spacing = 2.3  # 节点间距

        # 1️⃣ 创建节点
        for i in range(5):
            rect = RoundedRectangle(
                width=node_width,
                height=node_height,
                corner_radius=0.12,
                stroke_color=BLUE,
                fill_opacity=0
            )
            rect.move_to(RIGHT * i * spacing)

            label = Text(str(i + 1), font_size=30)  # node 数字大小
            label.move_to(rect.get_center())
            label.set_z_index(1)

            nodes.append(rect)
            labels.append(label)

        # 节点整体居中
        VGroup(*nodes, *labels).move_to(ORIGIN)

        # 2️⃣ 显示节点和标签
        self.add(*nodes)
        self.add(*labels)

        # 3️⃣ 顺序播放节点高亮 + 箭头（指针暂时不出现）
        for i in range(len(nodes) - 1):
            # 当前节点高亮
            self.play(
                # nodes[i].animate.set_fill(TEAL_E, opacity=0.85), 
                run_time=0.4
            )

            # 创建箭头（不销毁）
            arrow = Arrow(
                nodes[i].get_right(),
                nodes[i + 1].get_left(),
                buff=0.02,
                stroke_width=6,
                color=TEAL_E,
                max_tip_length_to_length_ratio=0.25
            )
            
            arrows.append(arrow)
            self.play(Create(arrow), run_time=0.4)

        # 最后一个节点高亮
        self.play(
            nodes[-1].animate.set_fill(TEAL_E, opacity=0.85),
            run_time=0.4
        )

        self.wait(0.5)

        # 4️⃣ 遍历指针出现，放在第一个节点下方
        pointer = Arrow(
            start=DOWN * 1.6,   # 指针长度加大
            end=ORIGIN,
            color=GOLD_D,
            stroke_width=8,     # 指针更粗
            max_tip_length_to_length_ratio=0.4
        )
        pointer.next_to(nodes[0], DOWN, buff=0.15)
        self.add(pointer)  # 直接显示指针

        # 5️⃣ 指针依次滑动到每个节点
        for i in range(1, len(nodes)):
            self.play(
                pointer.animate.next_to(nodes[i], DOWN, buff=0.15),
                run_time=0.6
            )

        self.wait(1)
