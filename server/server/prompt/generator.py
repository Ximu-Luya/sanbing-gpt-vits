class ThoughtChainPromptGenerator:
    """
    一个生成思维链提示词的类，包含目标、约束、资源三个部分，
        每个部分都可以有多个元素，最后生成的提示词会包含所有部分的所有元素。
    """
    def __init__(self):
        self.goals = []
        self.constraints = []
        self.resources = []

    def add_goal(self, target):
        self.goals.append(target)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def add_resource(self, resource):
        self.resources.append(resource)
    
    def _generate_numbered_list(self, items):
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])

    def generate_prompt(self):
        return (
            f"Resources:\n{self._generate_numbered_list(self.resources)}\n\n"
            f"Goals:\n{self._generate_numbered_list(self.goals)}\n\n"
            f"Constraints:\n{self._generate_numbered_list(self.constraints)}\n\n"
        )


# 测试用例
if __name__ == "__main__":
    generator = ThoughtChainPromptGenerator()
    print(generator.generate_prompt())