def des2Node(des):
    if des in ['<program>', '<block>', '<dblock>', '<ifblock>', '<lblock>', '<bblock>']:
        return DerivationTree(des, [])
    elif des == '<inst*>':
        return DerivationTree(des, None)


class DerivationTree:
    def __init__(self, name, children, annotation=None) -> None:
        self.name = name
        self.children = children
        self.annotation = annotation
        self._is_leaf = self.children is None
        self.need_expansion = (not self._is_leaf) and len(self.children) == 0
        self._has_possible_expansion = None
        self.last_possible_expansion_num = None
        self.occur_expansion_before_cal_has_expansion = False

    def max_depth(self):
        if self.is_leaf():
            return 0
        else:
            return 1 + max(child.max_depth() for child in self.children)

    def total_node_num(self):
        if self.is_leaf():
            return 1
        else:
            return 1 + sum(child.total_node_num() for child in self.children)

    def set_children(self, children):
        assert len(self.children) == 0, print(self.children)
        self.children = children
        self._is_leaf = False
        self.need_expansion = False

    def possible_expansion_num(self):
        return self.cal_possible_expansion_num()
            
    def cal_possible_expansion_num(self):
        if self._has_possible_expansion is None:
            self._has_possible_expansion = self._determine_has_possible_expansion()
            
        if not self._has_possible_expansion:
            return 0
        if self._is_leaf:
            return 0
        if self.need_expansion:
            return 1
        
        return sum(child.possible_expansion_num() for child in self.children)

    def has_possible_expansion(self):
        if self._has_possible_expansion is None:
            self._has_possible_expansion = self._determine_has_possible_expansion()
        if not self._has_possible_expansion:
            result =  False
        else:
            self._has_possible_expansion = self._determine_has_possible_expansion()
            result = self._has_possible_expansion
        return result

    # def 

    def _determine_has_possible_expansion(self):
        if self._is_leaf:
            return False
        if self.need_expansion:
            return True
        for child in self.children:
            if child.has_possible_expansion():
                return True
        return False

    def is_leaf(self) -> bool:
        return self._is_leaf

    def __repr__(self):
        return self.name


def print_tree(tree: DerivationTree, depth=0):
    print(' ' * depth, tree)
    if tree.is_leaf():
        return
    for child in tree.children:
        print_tree(child, depth + 1)
