from manim import *

class PartitionList(Scene):
    def construct(self):
        # 配置数据
        x_val = 3
        original_values = [1, 4, 3, 2, 5, 2]
        small_values = [v for v in original_values if v < x_val]
        big_values = [v for v in original_values if v >= x_val]

        # 创建原始链表
        original_group = self.create_linked_list(original_values, node_color=WHITE)
        original_group.to_edge(UP, buff=1.0)
        self.play(Create(original_group), run_time=1.5)
        self.wait(0.5)

        # 显示 x = 3（使用 MathTex，因为你有 LaTeX）
        x_eq = MathTex(r"x = 3", font_size=48, color=YELLOW)
        x_eq.next_to(original_group, DOWN, buff=0.8)
        self.play(Write(x_eq))
        self.wait(0.5)

        # 向上指示箭头（起点在下方，终点指向原始链表底部）
        down_arrow = Arrow(
            original_group.get_bottom() + DOWN * 1.2,
            original_group.get_bottom(),
            buff=0.1,
            stroke_width=4
        )
        self.play(Create(down_arrow))
        self.wait(0.5)

        # 创建分区后的两个链表
        small_group = self.create_linked_list(small_values, node_color=YELLOW)
        big_group = self.create_linked_list(big_values, node_color=RED)

        # 布局：左右分布
        small_group.shift(DOWN * 1.5 + LEFT * 3.0)
        big_group.shift(DOWN * 1.5 + RIGHT * 3.0)

        # 标签
        small_label = Text("值 < x", font_size=26, color=YELLOW)
        big_label = Text("值 ≥ x", font_size=26, color=RED)
        small_label.next_to(small_group, UP, buff=0.6)
        big_label.next_to(big_group, UP, buff=0.6)

        # 动画：同时显示两组
        self.play(
            Create(small_group),
            Create(big_group),
            Write(small_label),
            Write(big_label),
            run_time=1.5
        )
        self.wait(2)

    def create_linked_list(self, values, node_color=WHITE):
        """创建一个水平链表 VGroup（包含节点和箭头）"""
        if not values:
            return VGroup()

        nodes = []
        arrows = []

        # 创建所有节点
        for i, val in enumerate(values):
            # 节点框
            box = RoundedRectangle(
                width=1.0,
                height=0.6,
                corner_radius=0.1,
                stroke_color=node_color,
                stroke_width=2,
                fill_color=node_color,
                fill_opacity=0.2
            )
            # 值文本
            label = Text(str(val), font_size=28, color=WHITE)
            node = VGroup(box, label)
            nodes.append(node)

        # 水平排列节点
        group = VGroup(*nodes).arrange(RIGHT, buff=0.8)

        # 创建连接箭头
        for i in range(len(nodes) - 1):
            start = nodes[i].get_right()
            end = nodes[i + 1].get_left()
            arrow = Arrow(start, end, buff=0.1, stroke_width=2, max_tip_length_to_length_ratio=0.15)
            arrows.append(arrow)

        return VGroup(group, *arrows)